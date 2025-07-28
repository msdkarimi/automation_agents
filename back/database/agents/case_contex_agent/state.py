import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from typing_extensions import TypedDict, Optional
from typing import Annotated, Dict, List
from langchain_core.messages import AnyMessage, AIMessage, ToolCall, ToolMessage
from langgraph.graph.message import add_messages
import re
from agent_memory.models import OrdersSchema, PurchaseSchema, PaymentSchema, SOPCatalogSchema, ItemSchema
from pydantic import BaseModel, Field

def add_message_batches_reducer(x: List[List[AnyMessage]], y: List[List[AnyMessage]]) -> List[List[AnyMessage]]:
    return x + y


class CaseContextState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]
    used_tools: Annotated[list[list[ToolCall]], add_message_batches_reducer]
    used_tools_results: Annotated[list[list[ToolMessage]], add_message_batches_reducer]
    list_of_ordered_items: Optional[Annotated[dict[str, dict],  Field(description="This is a dictionary of ordered items by the given customer.")
    ]] = {}
    list_of_sops: Optional[dict[str, dict]] = {}
    customer_comment: str
    customer_id: str
    link_id: Optional[int] = None
    ticket_id: Optional[int] = None
    sop_id: Optional[str] = None
    purchase_id: Optional[str] = None
    order_id: Optional[str] = None
    payment_id: Optional[str] = None
    purchase: Optional[dict] = {}
    order: Optional[dict] = {}
    payment: Optional[dict] = {}
    sop: Optional[dict] = {}


class ReactAIMessage(AIMessage):
    @property
    def agent_response(self) -> str:
        # Remove the <think>...</think> block, return final answer
        return re.sub(r"<think>.*?</think>", "", self.content, flags=re.DOTALL).strip()

    @property
    def thought(self) -> str:
        # Extract <think>...</think> content
        match = re.search(r"<think>(.*?)</think>", self.content, flags=re.DOTALL)
        return match.group(1).strip() if match else ""
    