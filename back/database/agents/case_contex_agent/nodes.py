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
    

    _prompt_template_  = f"""
        **Agent Execution Context**

        **1. Current State Variables:**
        Review the following variables to understand what information is currently available. A `None` value indicates the ID has not been found yet.

        - ticket_id: {state.ticket_id}
        - customer_id: {state.customer_id}
        - customer_comment: {state.customer_comment}
        - order_id: {state.order_id}
        - item_id: {state.item_id}
        - purchase_id: {state.purchase_id}
        - payment_id: {state.payment_id}
        - sop_id: {state.sop_id}

        **2. Core Directives:**

        - **Analyze Conversation History:** Always examine the prior steps in the conversation to understand which tools have already been called and what their outputs were. Avoid redundant actions.

        - **Identify the Correct Order:** Customers may have multiple orders. You must use the `customer_comment` to accurately identify the specific order the customer is referring to before using tools that require an `order_id` or `item_id`.
        """

    instruction_template = f"""
    You are an intelligent assistant for processing customer service tickets.
    Your main goal is to accurately diagnose the customer's issue and link all relevant information (such as orders, purchases, payments, and procedural documents) to the support ticket.

    Your task is to analyze the customer's comment and decide which tools to use to gather the necessary IDs. Your process will conclude with a final call to the `update_linked_information_database` tool to save your findings.

    **Your Guiding Objective:**
    Work towards gathering all the necessary arguments (`ticket_id`, `sop_id`, `purchase_id`, `order_id`, `payment_id`) to make a successful final call to `update_linked_information_database`.

    **Tool Reference & Strategy:**

    * **To Investigate Orders:**
        - If the customer's comment is vague about which order they're referring to, use `get_customer_all_orders` to see their full purchase history.
        - After you identify the correct item from the list, use `update_item_state` to confirm your choice. This is important as it makes the `order_id` and `item_id` available for other tools.

    * **To Get Transaction Details:**
        - To find the `purchase_id` for an item, use `get_purchase_by_customerId_itemId`.
        - If the issue is about a charge, refund, or payment status, use `get_payment_by_customer_order_purchase` to get the `payment_id`.

    * **To Find the Correct Procedure:**
        - To understand the available solutions, use `get_list_of_sop_catalogs` to see all Standard Operating Procedures (SOPs).
        - Once you've matched the customer's problem to a procedure, use `update_sop_state` to select it and get the `sop_id`.

    * **To Complete the Task:**
        - The **final step** is always to call `update_linked_information_database`. Use this tool only when you have gathered all relevant IDs based on the nature of the customer's issue.
        - **Provide Summary:** After the database is updated, present a concise, user-friendly summary of the findings and actions taken. For example: "I've identified the issue with order #12345 regarding a refund. I have linked the corresponding payment and purchase IDs to the ticket and flagged it for the 'Defective Item Return' procedure. The finance team will now process the refund."
        - **End Process:** Conclude your work by outputting `**END**`.
    
    

    **Core Principles:**
    - **Autonomy:** You decide the best sequence of tool calling based on the customer's message and the state of the context.
    - **Efficiency:** Do not call a tool if you already have the information. For example, if a `purchase_id` is already set, there is no need to use tools to find it.
    - **Dependencies:** Be aware that some tools require information from others (e.g., you need an `item_id` to get a `purchase_id`). Plan your tool calls accordingly.
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

    if state.last_routing == 'reflex':
        messages += state.messages[-1:]

    response = graph.llm_with_tools.astream(messages, graph.thread_config)

    _tool_call_chunks = list()
    _final_response = None

    _think = False

    async for chunk in response:
        # print(chunk)
        if chunk.tool_call_chunks:
            _tmp = chunk
            _tool_call_chunks.extend(_tmp.tool_call_chunks)

        if isinstance(chunk, AIMessageChunk):

            # if _final_response is None:
            #     _final_response = chunk
            # else:
            #     _final_response += chunk

            yield {'stream_messages': chunk}
            if '<think>' in chunk.content or _think:
                _think = True
            if '</think>' in chunk.content or _think:
                _think = False
            if not _think and '</think>' not in chunk.content:
                
                if _final_response is None:
                    _final_response = chunk.content
                else:
                    _final_response += chunk.content

    if _final_response is not None:
        yield {'messages': AIMessage(content=_final_response)}
    
    if len(_tool_call_chunks):
        _calls = []
        for tool_call in _tool_call_chunks:
            _calls.append([ToolCall(**tool_call)])
        yield  {'used_tools': _calls, 'last_routing': 'tool'}
    else:
        if "END" in _final_response:
            yield {'last_routing': 'END'}
        else:
            yield  {'messages': [AIMessage(_final_response)], 'last_routing': 'reflex'}

async def check_agent_action(state):

    print('negin', state.messages[-1:])
    print('negin', state.messages)

    if state.last_routing == 'tool':
        return 'tool'
    elif state.last_routing == 'reflex':
        return 'reflex'
    else:
        return 'final'
    
    # if len(state.used_tools) != len(state.used_tools_results):
    #     return 'tool'
    # elif 'END' not in state.messages[-1].content:
    #     return 'loop'
    # else:
    #     return 'final'

    
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
                    if result.get('used_tools_results', None) and result['used_tools_results'].get('tool_output', None):
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
    print('lastt', state.ticket_id)
    
    response = await get_ticket_link_by_id_controller(ticket_id=state.ticket_id)
    
    if isinstance(response, int):
        if response >= 0:
            _response = insert_new_ticket_linke_controller(ticket_id=state.ticket_id)

            if _response == 0:
                yield {'status': 'success' }
            else:
                yield {'status': 'error'}

        else:
            yield {'status': 'there is problemt with connection to database, please check the database connection.'}

    else:
        _content = {'ticket_id':response.ticket_id,
                    'link_id': response.id,
                    'sop_id': response.sop_id,
                    'purchase_id': response.purchase_id, 
                    'order_id': response.order_id,
                    'payment_id': response.payment_id
                    }
        
        yield _content
