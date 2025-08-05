import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from database.agent_memory.models import IgniteCaseContextAgentSchema
from database.agents.case_contex_agent.graph import producer
from fastapi import APIRouter,  Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from langchain_ollama.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
import re
import uuid
import asyncio
from typing import Dict
import json
from shared import redis_client






agent_bp = APIRouter(prefix="/agents")
_tmp = None 

async def _generator(prompt: IgniteCaseContextAgentSchema):

    async for chunk in producer(**prompt.dict()):
        yield f"data: {json.dumps(chunk)} \n\n"

    yield "data: [DONE] \n\n"

@agent_bp.post("/case_context")
async def init_chat_case_context(prompt: IgniteCaseContextAgentSchema):
    request_id = str(uuid.uuid4())
    _prompt = prompt.json()
    await redis_client.set(request_id, _prompt, ex=300)
    return {"request_id": request_id}
 


@agent_bp.get("/case_context/stream/{stream_id}")
async def stream_events(stream_id: str, request: Request):
    """Retrieves prompt from Redis and streams the LLM response."""
    prompt = await redis_client.get(stream_id)
    prompt = IgniteCaseContextAgentSchema.parse_raw(prompt)
    if prompt is None:
        async def error_generator():
            yield "data: Error: Invalid or expired request ID.\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(error_generator(), media_type="text/event-stream")

    # return StreamingResponse(llm_stream_generator(prompt.dict()), media_type="text/event-stream")
    return StreamingResponse(_generator(prompt), media_type="text/event-stream")
