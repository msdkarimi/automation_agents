import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from langgraph.graph import StateGraph, START, END
from base_agent import BaseAgent
from state import CaseContextState
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from tools import get_all_tools
from langchain_ollama.chat_models import ChatOllama
from nodes import agent_node, check_agent_action, tool_calling_node
from functools import partial
from langgraph.checkpoint.memory import InMemorySaver
from collections import defaultdict

class CaseContectGraph(BaseAgent):
    def __init__(self, 
                 model='qwen3:1.7b', 
                 ollama_base_url='http://localhost:11434', 
                 config=None,
                 tools=None):

        
        self.llm = ChatOllama(base_url=ollama_base_url, model=model, temperature=0.0)
        self.tools = tools
        self.llm_with_tools = self.llm.bind_tools(self.tools) if tools else None

        self.thread_config = config or {"configurable": {"thread_id": "1"}}

        self.all_nodes = dict()
        self.all_edges = dict()
        self.conditional_edges = dict()

        self.tmp = f"""
                  You are a helpful and empathetic customer service agent. Your goal is to resolve customer issues efficiently.

                    You have access to the following tools:
                    <tools>
                    {self.tools}
                    </tools>

                    To solve the user's request, you must use the following thinking process and format. You will be in a loop of Thought, Action, Action Input, and Observation.

                    1.  **Thought:** First, think step-by-step about the user's request. Break down the problem. Analyze the information you have and what you need. Decide if you need to use a tool and which one is most appropriate. This is your Chain of Thought.
                    2.  **Action:** The name of the tool you have decided to use. This must be one of the tools listed above: [{self.tools}].
                    3.  **Action Input:** The JSON input for the selected tool, matching its schema.
                    4.  **Observation:** After you provide an action, the system will execute it and give you back an observation.

                    If you have gathered enough information to provide a final answer to the user, you must use the special action `Finish` with the key "answer" in the `action_input`.

                    Let's begin.
                        """


    def add_new_node(self, node_name, the_node):
        self.all_nodes[node_name] = the_node

    def add_new_edge(self, source_node, target_node):
        self.all_edges[source_node] = target_node
    
    def add_new_conditional_edge(self, source_node, condition_node, target_nodes):
        self.conditional_edges[source_node] = {condition_node : target_nodes}


    def _build_graph(self):
        assert len(self.all_nodes) != 0, f'the list of nodes is empty, please provide nodes and the names using {self.add_new_node.__name__} function.'
        assert len(self.all_edges) != 0, f'the list of edges is empty, please provide edges using  {self.add_new_edge.__name__} function.'
        
        _builder = StateGraph(CaseContextState)

        for node_name, the_node in self.all_nodes.items():
            _builder.add_node(node_name, the_node)

        for source_node, target_node in self.all_edges.items():
            _builder.add_edge(source_node, target_node)

        for source_node, condition_node in self.conditional_edges.items():
            condition_node, target_nodes = next(iter(self.conditional_edges[source_node].items())) 
            _builder.add_conditional_edges(source_node, condition_node, target_nodes)

        self.graph = _builder.compile(checkpointer=InMemorySaver())

    
    
    
    def invoke_agent(self):
        res = agent.graph.invoke({'customer_comment': "Payment for a Dyson V15 vacuum ($700) was declined, but the amount was deducted. No order confirmation received. Please refund or process.",
                                  'ticket_id': 1,
                                  'customer_id': 'CUST10002',
                                  'messages': [
                                      
                                    # AIMessage(self.tmp)
                                      SystemMessage(f"""You are a careful and helpful assistant responsible for handling user support tickets. Your role is to assist in resolving ticket-related issues by analyzing the provided case context and using the available tools effectively.
                                                                You act as a **case context agent** in a ticketing system. Use the provided context to understand the situation and determine what actions are needed.
                                                                Your goals:
                                                                - Carefully analyze the available context and customer comment.
                                                                - Clearly state what decisions you make and **why** you made them.
                                                                - If additional information is needed, use the correct tools and explain the purpose of each tool call.
                                                                - Be concise, accurate, and professional.

                                                                Always base your decisions on the data in the context. Do not ask for information that is already provided.
                                                                """)



                                                ]}, self.thread_config)
        print(res)

    def save_state(self):
        pass

    def load_state(self, user_id):
        pass


    def print_graph(self, ):
        png_data = self.graph.get_graph().draw_mermaid_png()
        with open("graph.png", "wb") as f:
            f.write(png_data)

    
    
        


agent = CaseContectGraph(model='qwen3:8b', tools=get_all_tools())
# agent = CaseContectGraph(tools=get_all_tools())


agent.add_new_node("entry_point", partial(agent_node, agent))
agent.add_new_node("tool_node",  partial(tool_calling_node, agent))

agent.add_new_edge(START, "entry_point")
agent.add_new_edge('tool_node', "entry_point")



agent.add_new_conditional_edge('entry_point', check_agent_action, {'tool':'tool_node', 'final':END})

agent._build_graph()

agent.invoke_agent()
