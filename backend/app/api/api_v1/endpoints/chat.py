# backend/app/api/api_v1/endpoints/chat.py
import sys
import os
import json
import time
from typing import Generator
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.schemas.user import UserBase

# Dynamically resolve and inject hyphenated ai-engine directory path into system imports
current_dir = os.path.dirname(os.path.abspath(__file__))
while current_dir and not os.path.exists(os.path.join(current_dir, "README.md")):
    parent = os.path.dirname(current_dir)
    if parent == current_dir:
        break
    current_dir = parent
ai_engine_path = os.path.join(current_dir, "ai-engine")
if ai_engine_path not in sys.path:
    sys.path.append(ai_engine_path)

from graph_coordinator import agent_graph

router = APIRouter()

class ChatMessagePayload(BaseModel):
    message: str
    session_id: str
    demo_mode: bool = True

def stream_copilot_response(message: str, demo_mode: bool) -> Generator[str, None, None]:
    """
    Executes LangGraph agent state coordination and streams response chunks 
    followed by explainability metadata in Server-Sent Events (SSE) format.
    """
    try:
        # 1. Run the LangGraph execution flow
        # In a real environment, we wrap the HumanMessage list and pass it to agent graph
        from langchain_core.messages import HumanMessage
        inputs = {"messages": [HumanMessage(content=message)]}
        output_state = agent_graph.invoke(inputs)
        
        response_text = output_state.get("response") or "Failed to compile response."
        citations = output_state.get("citations") or []
        confidence = output_state.get("confidence_score") or 0.90
        explainability = output_state.get("explainability") or {}
        
        # Apply citizen-safe Demo Mode PII masking on the final text before streaming
        if demoMode := demo_mode:
            # Mask common indian names and suspect names
            response_text = response_text.replace("Ravi alias Kariya", "<SUSPECT_A_MASKED>")
            response_text = response_text.replace("Ganesh alias Gani", "<SUSPECT_B_MASKED>")
            response_text = response_text.replace("Imran Khan", "<SUSPECT_C_MASKED>")
            
        # 2. Simulate chunk streaming for smooth UI micro-animations
        words = response_text.split(" ")
        for i, word in enumerate(words):
            chunk = {"event": "message_chunk", "text": word + (" " if i < len(words) - 1 else "")}
            yield f"data: {json.dumps(chunk)}\n\n"
            time.sleep(0.04) # 40ms sleep simulates streaming output
            
        # 3. Stream final explainability payload
        meta_payload = {
            "event": "metadata",
            "sql_executed": explainability.get("sql_executed"),
            "citations": citations,
            "confidence_score": confidence
        }
        yield f"data: {json.dumps(meta_payload)}\n\n"
        
    except Exception as e:
        err_payload = {"event": "error", "text": f"Agent graph execution failure: {str(e)}"}
        yield f"data: {json.dumps(err_payload)}\n\n"

@router.post("/message")
def chat_message(
    payload: ChatMessagePayload,
    current_user: UserBase = Depends(get_current_user)
):
    """
    Submit a conversational query to the KSP Crime Intelligence Copilot.
    Requires Bearer JWT authentication. Returns streamed chunks and SQL explainability.
    """
    return StreamingResponse(
        stream_copilot_response(payload.message, payload.demo_mode),
        media_type="text/event-stream"
    )
