import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolCall, ToolMessage
from case_contex_agent.state import ReactAIMessage
from langchain.prompts import PromptTemplate
from langchain_core.tools import StructuredTool as SyncStructuredTool
from langchain_core.tools.structured import StructuredTool as AsyncStructuredTool
import json
import uuid
from langchain_core.messages.ai import AIMessageChunk
from case_contex_agent.state import CaseContextState

from agent_memory.controllers.ticket_links_controllers import get_ticket_link_by_id_controller, insert_new_ticket_linke_controller
from agent_memory.controllers.orders_catalog_controllers import get_orders_by_customer_id_controller


async def agent_node(graph, state:CaseContextState)-> CaseContextState:
    

    _prompt_template_ = f"""
                            Here is the current context and available variables:

                            - order_id: {state.order_id}
                            - payment_id: {state.payment_id}
                            - sop_id: {state.sop_id}
                            - purchase_id: {state.purchase_id}
                            - ticket_id: {state.ticket_id}
                            - customer_comment: {state.customer_comment}
                            - customer_id: {state.customer_id}

                            always look at the convesation input to better understand which tools has been called to so far.
                            consider that a customer migh have multiple orders, based on this and the customer comment, you have to identify the correct order.

                        """


    instruction_template = f"""
    You are a supportive assistant for resolving customer service tickets related to specific order. 
    Your main goal is to accurately diagnose the customer's issue and attach all relevant information to the ticket.

    To do this, you must:

    - **Analyze the customer's comment** to identify key details.
    - **Use your tools** to find any missing information based on current context and available variables.
    - **Link all relevant data** to the ticket.

    Always prioritize efficiency. Only use tools when it's absolutely necessary to gather information that isn't already available from previous steps or tool outputs.
    Avoid unnecessary tool calls to streamline the process.
    """

    messages = [SystemMessage(instruction_template)]

    if len(state.used_tools_results):
        _calls = []
        for idx, _msg in enumerate(state.used_tools_results):
            _calls.append(AIMessage(content="" , used_tools=state.used_tools[idx]))
            _calls.append(_msg[-1])
        messages += _calls
        # print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

    messages += [HumanMessage(_prompt_template_)]

    response = graph.llm_with_tools.astream(messages, graph.thread_config)

    _tool_call_chunks = list()
    _final_response = None

    async for chunk in response:
        # print(chunk)
        if chunk.tool_call_chunks:
            _tmp = chunk
            _tool_call_chunks.extend(_tmp.tool_call_chunks)

        if isinstance(chunk, AIMessageChunk):

            if _final_response is None:
                _final_response = chunk
            else:
                _final_response += chunk

            yield {'stream_messages': chunk}
    
    if len(_tool_call_chunks):
        _calls = []
        for tool_call in _tool_call_chunks:
            _calls.append([ToolCall(**tool_call)])
        yield  {'used_tools': _calls,}
    else:
        pass
        # yield  {'messages': [AIMessage(_final_response)]}

async def check_agent_action(state):
    
    if len(state.used_tools) != len(state.used_tools_results):
        return 'tool'
    else:
        return 'final'

    
async def tool_calling_node(graph, state:CaseContextState):
    
    tool_results = list()
    return_values = dict()
    for tool_call in state.used_tools[-1]:
        
        tool_name = tool_call.get("name")
        tool_args = json.loads(tool_call.get("args", '{}'))
        tool_call_id = tool_call.get("id")

  

        for tool in graph.tools:
            if tool.name == tool_name:  # Match tool by name
                try:
                    print('**************************CALLED**************************',tool.name, tool_args, type(tool))
                    if isinstance(tool, SyncStructuredTool):
                        result = tool.invoke(tool_args)  # for sync
                    elif isinstance(tool, AsyncStructuredTool):
                        result = await tool.ainvoke(tool_args)  # for async
                    else:
                        result = tool(**tool_args)  # Fallback for raw functions
                    
                    if isinstance(result['used_tools_results']['tool_output'], dict):
                        return_values.update(result['used_tools_results']['tool_output'])

                    tool_results.append(ToolMessage(
                        content=str(result['used_tools_results']['tool_output']),
                        tool_call_id=str(tool_call_id),
                        name=tool_name,
                        status=str(result['used_tools_results']['status']),
                        type="tool",
                    ))

                except Exception as e:
                    print('in exception')
                    tool_results.append(
                        ToolMessage(
                            content=f"Error: {str(e)}",
                            tool_call_id=tool_call_id,
                            name=tool_name,
                            status="error",
                            type="tool",
                        )
                    )
    return_values.update({'used_tools_results': [tool_results]})
    return return_values

async def get_ticket_details_node(state: CaseContextState) -> dict:
    
    """this function is used to see if any link is created to given ticket_id or not.
    Args:
        ticket_id (int)
    Returns:
        In case of success, it returns keys related to the state of given link to ticket which is compatible with CaseContextState type.
        In case of failure it provides the reasoning. 
    """
    
    response = await get_ticket_link_by_id_controller(ticket_id=state.ticket_id)
    
    if isinstance(response, int):
        if response > 0:
            response = insert_new_ticket_linke_controller(ticket_id=state.ticket_id)

            if response == 0:
                yield {'used_tools_results': {'status': 'success', 'tool_output': f'link for the ticket_id={state.ticket_id} is created' }}
            else:
                yield {'used_tools_results': {'status': 'error'}}

        else:
            yield {'used_tools_results': {'status': 'there is problemt with connection to database, please check the database connection.'}}

    else:
        _content = {'ticket_id':response.ticket_id,
                    'link_id': response.id,
                    'sop_id': response.sop_id,
                    'purchase_id': response.purchase_id, 
                    'order_id': response.order_id,
                    'payment_id': response.payment_id
                    }
        
        yield _content
