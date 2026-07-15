# backend/tests/test_ai_agent.py
import sys
import os

# Inject dynamic path to load the ai-engine sibling directory
current_dir = os.path.dirname(os.path.abspath(__file__))
ai_engine_path = os.path.abspath(os.path.join(current_dir, "../../ai-engine"))
if ai_engine_path not in sys.path:
    sys.path.append(ai_engine_path)

from sql_agent import is_safe_query, generate_sql_query
from graph_coordinator import agent_graph

def test_sql_guardrails_blocks_unsafe():
    """Verify that SQL engine blocks write/update operations to preserve read-only constraints."""
    assert is_safe_query("SELECT * FROM CaseMaster;") is True
    assert is_safe_query("WITH recent AS (SELECT * FROM CaseMaster) SELECT * FROM recent;") is True
    
    # Check blocked operations
    assert is_safe_query("INSERT INTO CaseMaster (CrimeNo) VALUES ('123');") is False
    assert is_safe_query("UPDATE CaseMaster SET PoliceStationID = 1;") is False
    assert is_safe_query("DROP TABLE CaseMaster;") is False
    assert is_safe_query("ALTER TABLE CaseMaster ADD COLUMN test VARCHAR;") is False
    assert is_safe_query("CREATE TABLE TestTable (id INT);") is False

def test_rule_based_sql_generation():
    """Verify keyword query translation rules work correctly."""
    q1 = generate_sql_query("Show theft cases in Kalasipalya")
    assert "CrimeMajorHeadID = 2" in q1
    
    q2 = generate_sql_query("Show cases linked to id 101")
    assert "CaseMasterID = 101" in q2

def test_langgraph_agent_execution():
    """Verify compiled LangGraph state workflow executes and returns coordinated synthesis reports."""
    from langchain_core.messages import HumanMessage
    
    inputs = {"messages": [HumanMessage(content="Show theft cases in Kalasipalya")]}
    output_state = agent_graph.invoke(inputs)
    
    assert "response" in output_state
    assert "confidence_score" in output_state
    assert "explainability" in output_state
    assert "citations" in output_state
    
    assert output_state["confidence_score"] >= 0.50
    assert "sql_executed" in output_state["explainability"]
