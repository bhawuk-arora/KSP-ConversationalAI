# ai-engine/graph_coordinator.py
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END

from agent_state import AgentState
from sql_agent import generate_sql_query, run_sql_query
from vector_agent import search_vector_briefs

def router_node(state: AgentState) -> Dict[str, Any]:
    """
    Evaluates state and determines whether to query relational Postgres metrics (SQL) 
    or scan unstructured narratives in Qdrant (Vector).
    """
    messages = state.get("messages", [])
    if not messages:
        return {"next_agent": "synthesis"}
        
    last_msg = messages[-1].content.lower()
    
    # Heuristics routing rules
    if any(keyword in last_msg for keyword in ["facts", "details", "narrative", "summarize", "happen"]):
        return {"next_agent": "vector"}
    return {"next_agent": "sql"}

def sql_agent_node(state: AgentState) -> Dict[str, Any]:
    """Translates query to SQL, executes it, and registers results."""
    messages = state.get("messages", [])
    last_msg = messages[-1].content
    
    sql = generate_sql_query(last_msg)
    results = run_sql_query(sql)
    
    return {
        "sql_query": sql,
        "query_results": results,
        "next_agent": "synthesis"
    }

def vector_agent_node(state: AgentState) -> Dict[str, Any]:
    """Vectorizes facts query and searches Qdrant."""
    messages = state.get("messages", [])
    last_msg = messages[-1].content
    
    results = search_vector_briefs(last_msg)
    
    return {
        "vector_results": results,
        "next_agent": "synthesis"
    }

def synthesis_node(state: AgentState) -> Dict[str, Any]:
    """Combines structured/unstructured dataset inputs and designs final response payload."""
    sql_query = state.get("sql_query")
    sql_results = state.get("query_results") or []
    vec_results = state.get("vector_results") or []
    
    citations = []
    response_text = ""
    confidence = 0.90
    
    # 1. Synthesize SQL details
    if sql_results:
        confidence = 0.95
        count = len(sql_results)
        response_text += f"I retrieved {count} relevant record(s) matching your request. "
        
        # Extract citations
        for row in sql_results:
            c_no = row.get("CrimeNo") or row.get("crimeno")
            if c_no:
                citations.append(c_no)
                
        # Format a brief text representation
        response_text += f"Records: {sql_results[:2]}"
        
    # 2. Synthesize Vector details
    elif vec_results:
        confidence = 0.88
        response_text += "Based on matching narrative facts: "
        for hit in vec_results:
            brief = hit.get("brief_facts")
            c_no = hit.get("crime_no")
            if c_no:
                citations.append(c_no)
            if brief:
                response_text += f"\n- [{c_no}] {brief[:120]}..."
                
    else:
        response_text = "I couldn't find any direct records or narrative overlaps matching your query in the database. Please try adjusting your parameters."
        confidence = 0.50
        
    explainability = {
        "sql_executed": sql_query,
        "qdrant_matches_count": len(vec_results),
        "db_rows_count": len(sql_results)
    }
    
    return {
        "response": response_text,
        "citations": list(set(citations)),
        "confidence_score": confidence,
        "explainability": explainability
    }

# Assemble LangGraph Workflow State
workflow = StateGraph(AgentState)

# Register Node blocks
workflow.add_node("sql_agent", sql_agent_node)
workflow.add_node("vector_agent", vector_agent_node)
workflow.add_node("synthesis", synthesis_node)

# Declare execution rules
workflow.set_entry_point("sql_agent") # Default routing baseline
workflow.add_edge("sql_agent", "synthesis")
workflow.add_edge("vector_agent", "synthesis")
workflow.add_edge("synthesis", END)

# Compile LangGraph Coordinator
agent_graph = workflow.compile()
