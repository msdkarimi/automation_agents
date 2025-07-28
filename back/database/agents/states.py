from typing_extensions import TypedDict
from typing import Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class CustomMessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    prompt: str
    summary:str