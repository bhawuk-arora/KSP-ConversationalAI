# ai-engine/agent_state.py
from typing import TypedDict, List, Annotated, Dict, Any, Optional
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    Represents the state of the Conversational Agent throughout the LangGraph workflow.
    """
    messages: Annotated[list, add_messages]  # Stateful chat conversation feed
    sql_query: Optional[str]                  # Generated SQL query string
    query_results: Optional[List[Dict[str, Any]]] # Result dataset retrieved from Postgres
    vector_results: Optional[List[Dict[str, Any]]] # Narrative context chunks matched in Qdrant
    response: Optional[str]                   # Final compiled output response text
    confidence_score: Optional[float]          # Calculated confidence index
    citations: Optional[List[str]]             # Citation source codes (e.g. Case IDs)
    explainability: Optional[Dict[str, Any]]   # Compilation statistics for frontend panels
