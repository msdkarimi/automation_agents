import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from langgraph.graph import StateGraph, START, END
from base_agent import BaseAgent
from case_contex_agent.state import CaseContextState
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.messages.ai import AIMessageChunk
from case_contex_agent.tools import get_all_tools
from langchain_ollama.chat_models import ChatOllama
from case_contex_agent.nodes import agent_node, check_agent_action, tool_calling_node, get_ticket_details_node
from functools import partial
from langgraph.checkpoint.memory import InMemorySaver
from collections import defaultdict

# back\database\agents\case_contex_agent

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

    
    
    
    def invoke_agent(self, ticket_id, customer_id, customer_comment):
        res = self.graph.invoke({'customer_comment': customer_comment,
                                  'ticket_id': ticket_id,
                                  'customer_id': customer_id }, self.thread_config)
        print(res)

    def stream_agent(self, prompt):
        for event in self.graph.stream(prompt, stream_mode=["updates", 'messages'], config=self.thread_config):
            update, message = event
            if isinstance(message, dict):
                print(message)

            elif isinstance(message[0], AIMessageChunk):
                print(message[0].content, end="", flush=True)
            
    async def astream_agent(self, prompt):
        yield {"type":"agent", "phase":"start", "id":"1234"}
        _is_think = False
        async for event in self.graph.astream_events(prompt, version="v1", config=self.thread_config):
            if event['event'] == 'on_chain_start' and event['name'] == 'agent_node':
                if event['data']:
                    yield {"type":"loop", "phase":"react", "id":event["run_id"]}

            kind = event["event"]
        
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk.content:
                    if chunk.content == '<think>':
                        _is_think = True
                        continue
                    elif chunk.content == '</think>':
                        _is_think = False
                        continue
                    if _is_think:
                        yield {"type":"chat", "content":str(chunk.content), "think":True, "phase":"generation", "id":event["run_id"]}
                        
                    else:
                        yield {"type":"chat", "content":str(chunk.content), "think":False, "phase":"generation", "id":event["run_id"]}
                        
                    
            if kind == "on_tool_start":
                yield {"type":"tool", "name":event["name"], "args":event["data"].get("input"), "phase":"start", "id":event["run_id"]}
                 
            if kind == "on_tool_end":
                yield {"type":"tool", "name":event["name"], "phase":"finish", "id":event["run_id"]}
                
        
        yield {"type":"agent", "phase":"finish", "id":"6789"}
        

    def save_state(self):
        pass

    def load_state(self, user_id):
        pass


    def print_graph(self, ):
        png_data = self.graph.get_graph().draw_mermaid_png()
        with open("agent_graph.png", "wb") as f:
            f.write(png_data)

async def producer(ticket_id, customer_id, customer_comment):
    # print(ticket_id, customer_id, customer_comment)

    agent = CaseContectGraph(model='qwen3:30b', tools=get_all_tools())
    
    agent.add_new_node("get_history", get_ticket_details_node)

    agent.add_new_node("agent_node", partial(agent_node, agent))
    agent.add_new_node("tool_node",  partial(tool_calling_node, agent))

    agent.add_new_edge(START, "get_history")
    agent.add_new_edge("get_history", "agent_node")
    agent.add_new_edge('tool_node', "agent_node")

    agent.add_new_conditional_edge('agent_node', check_agent_action, 
        {'tool':'tool_node',
        "reflex": "agent_node",
         'final':END}
    )

    agent._build_graph()

    
    
    async for _s in agent.astream_agent({'ticket_id':ticket_id, 'customer_id':customer_id, 'customer_comment':customer_comment, }):
        # print(_i, end='', flush=True)
        yield _s

if __name__ == "__main__":

    agent = CaseContectGraph(model='qwen3:30b', tools=get_all_tools())
    
    agent.add_new_node("get_history", get_ticket_details_node)

    agent.add_new_node("agent_node", partial(agent_node, agent))
    agent.add_new_node("tool_node",  partial(tool_calling_node, agent))

    agent.add_new_edge(START, "get_history")
    agent.add_new_edge("get_history", "agent_node")
    agent.add_new_edge('tool_node', "agent_node")

    agent.add_new_conditional_edge('agent_node', check_agent_action, 
        {'tool':'tool_node',
        "reflex": "agent_node",
         'final':END}
    )

    agent._build_graph()

    agent.print_graph()


    # import asyncio
    # asyncio.run(
    #     producer(1,
    #             'CUST10001',
    #             "Order #ORD50001: Charged twice for a 55-inch Samsung 4K TV ($600). Total shows $1200 on my card. Please refund one charge."
    # )
    # )
 