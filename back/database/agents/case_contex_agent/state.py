import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from typing_extensions import TypedDict, Optional
from typing import Annotated, Dict, List
from langchain_core.messages import AnyMessage, AIMessage, ToolCall, ToolMessage
from langgraph.graph.message import add_messages
from langchain_core.messages.tool import ToolCallChunk
from langchain_core.messages.ai import AIMessageChunk
import re
from agent_memory.models import OrdersSchema, PurchaseSchema, PaymentSchema, SOPCatalogSchema, ItemSchema
from pydantic import BaseModel, Field
import json

def add_message_batches_reducer(x: List[List[AnyMessage]], y: List[List[AnyMessage]]) -> List[List[AnyMessage]]:
    print(x)
    print(y)
    return x + y


class CaseContextState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]
    stream_messages: Annotated[list[AIMessage | AIMessageChunk], add_messages]
    used_tools: Annotated[list[list[ToolCall | ToolCallChunk]], add_message_batches_reducer]
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

    @classmethod
    def from_ai_message(cls, msg: AIMessage) -> "ReactAIMessage":
        return cls(content=msg.content, additional_kwargs=msg.additional_kwargs, example=msg.example)

    def _extract_field(self, field_name: str) -> str:
        """
        Extract the text after e.g. "Thought:" until a double newline or next field.
        """
        pattern = rf"{field_name}:\s*(.*?)(?=\n\n\S+:|$)"  # lookahead for next field or end
        match = re.search(pattern, self.content, flags=re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    @property
    def agent_thought(self) -> str:
        return self._extract_field("Thought")

    @property
    def agent_action(self) -> str:
        return self._extract_field("Action")

    @property
    def agent_action_input(self) -> dict:
        action_input_str = self._extract_field("Action_input")
        try:
            return action_input_str
        except json.JSONDecodeError:
            return {}

    @property
    def agent_output_for_human(self) -> str:
        return self._extract_field("Output_for_human")

    @property
    def agent_observation(self) -> str:
        return self._extract_field("Observation")