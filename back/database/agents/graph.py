
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from states import CustomMessagesState
from IPython.display import Image, display
from langgraph.checkpoint.memory import InMemorySaver
from nodes.normal_nodes import get_llm

from nodes.normal_nodes import interaction, just_print

import os

class Graph:
    def __repr__(self):
        png_data = graph.get_graph().draw_mermaid_png()
        with open(os.path.join(self.checkpoint_root, 'graph.png'), "wb") as f:
            f.write(png_data)
    
    def __init__(checkpoint_root, ):
        pass


if __name__ == "__main__":


   

    builder = StateGraph(CustomMessagesState)
    builder.add_node("node_1", interaction)
    builder.add_node("node_2", just_print)


    # Logic
    builder.add_edge(START, "node_1")
    builder.add_edge("node_1", "node_2")
    builder.add_edge("node_2", END)


    # Add
    memory = InMemorySaver()
    graph = builder.compile(checkpointer=memory)
    
    config = {"configurable": {"thread_id": "1"}}
    v = input('your prompt:')
    graph.invoke({'prompt': v, 'messages': [SystemMessage('you are a polite asistant to greeting peopl your name is Jafar.')]}, config)
    v = input('your prompt:')
    graph.invoke({'prompt': v}, config)

    v = input('your prompt:')
    graph.invoke({'prompt': v}, config)
    # print(graph.get_state(config))


    # # png_data = graph.get_graph().draw_mermaid_png()
    # # with open("graph.png", "wb") as f:
    # #     f.write(png_data)