# ai-engine/sql_agent.py
import re
from typing import Dict, Any, List
from sqlalchemy.sql import text
from app.core.database import SessionLocal

# Simple keywords mappings to mock SQL queries if no LLM API key is present
MOCK_SQL_RULES = [
    (r"\b(101|102|103|104|105|106)\b", 
     "SELECT * FROM CaseMaster WHERE CaseMasterID = :id_param;"),
    (r"\b(theft|burglary|stolen)\b", 
     "SELECT * FROM CaseMaster WHERE CrimeMajorHeadID = 2 LIMIT 5;"),
    (r"\b(murder|kill|stabbing)\b", 
     "SELECT * FROM CaseMaster WHERE CrimeMajorHeadID = 1 LIMIT 5;"),
    (r"\b(drugs|ndps|ganja)\b", 
     "SELECT * FROM CaseMaster WHERE CrimeMajorHeadID = 3 LIMIT 5;")
]

def generate_sql_query(user_query: str) -> str:
    """
    Translates user natural language queries into clean PostgreSQL read-only DDL syntax.
    Falls back to a keyword-based rule matcher if no LLM settings are available.
    """
    # 1. Check for API key and execute LLM (placeholder hook for later OpenAI/Gemini bindings)
    # import os
    # if os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY"):
    #     # Run LangChain model routing...
    #     pass
    
    # 2. Rule-based matcher fallback (ensures offline reliability)
    query_lower = user_query.lower()
    for pattern, sql in MOCK_SQL_RULES:
        match = re.search(pattern, query_lower)
        if match:
            if ":id_param" in sql:
                return sql.replace(":id_param", match.group(1))
            return sql
            
    # Default query fallback
    return "SELECT * FROM CaseMaster ORDER BY CrimeRegisteredDate DESC LIMIT 5;"

def is_safe_query(sql: str) -> bool:
    """Enforces read-only safety guardrails, blocking attempts to modify tables."""
    sql_clean = sql.upper().strip()
    
    # Block unsafe commands
    unsafe_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE", "REPLACE", "GRANT"]
    for keyword in unsafe_keywords:
        # Match word boundaries to prevent false positives (like table names containing characters)
        pattern = r"\b" + keyword + r"\b"
        if re.search(pattern, sql_clean):
            return False
            
    # Must start with SELECT or WITH
    if not (sql_clean.startswith("SELECT") or sql_clean.startswith("WITH") or sql_clean.startswith("EXPLAIN")):
        return False
        
    return True

def run_sql_query(sql: str) -> List[Dict[str, Any]]:
    """Runs a read-only SQL query on PostgreSQL and returns the dataset as a list of dicts."""
    if not is_safe_query(sql):
        raise ValueError("Unsafe SQL Query blocked by guardrails. Only SELECT statements are permitted.")
        
    db = SessionLocal()
    try:
        result = db.execute(text(sql))
        # Convert row mappings to list of dicts
        columns = result.keys()
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        return rows
    except Exception as e:
        # Fallback empty list on compilation error
        print(f"[SQL ERROR] Failed to run query: {e}")
        return []
    finally:
        db.close()
