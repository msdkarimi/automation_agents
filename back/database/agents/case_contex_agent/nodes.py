from state import CaseContextState
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolCall, ToolMessage
from tools import ReactAIMessage
from langchain.prompts import PromptTemplate
from langchain_core.tools import StructuredTool
import json



def agent_node(graph, state:CaseContextState)-> CaseContextState:

    # print('---------------')
    # print('agent node!!!!')
    # print('---------------')

    prompt_template = f"""
                        Here are context state and variables:
                            order_id: {state.order_id},
                            payment_id: {state.payment_id}, 
                            sop_id: {state.sop_id}, 
                            purchase_id: {state.purchase_id}, 
                            ticket_id: {state.ticket_id}, 
                            customer_comment: {state.customer_comment}, 
                            customer_id: {state.customer_id}, 
                            purchase: {state.purchase}, 
                            order: {state.order}, 
                            payment: {state.payment}, 
                            sop: {state.sop}
                        """
    instruction_template = f"""
                        Your tasks include:
                        - pay attention, based on customer comment you have to decide which fields need to be field using provided tools.
                        - first you have to make sure if there is any case context in the link ticked table, you can check this thanks to tool called get_ticket_details.
                        - then, link_id field value helps you to find out if there is any link entry or not for given ticket_id.
                        - if there is not you have to insert new entry into link ticket table, if there is which means link_id has value, you have to do following: 
                        - since customer might have many orders, based on list of ordered items and customer_comment you have to find the item information and order id related to customer_comment
                        list_of_ordered_items if is not empty, has this charachteristics: "order_id": "item information"
                        - based on customer comment you have to call any tools to fill any related missing information.
                        - since you're supposed to adress issues related to orders, if you do not have information related to order of user, it is recommended to start with fetching the order informatin based on the current state.
                        - then, based of available tools try to fill the **RELATED** missing information based on customer prompt.
                        Use the tools' documentation to select the correct tool and provide valid arguments. Respond concisely and professionally.
                        tool calling results: shows the history of tool callings and the corresponding outputs.
                        you have to fill all missing values in the context by provided tools.
                        """
    
    # prompt = PromptTemplate(template=prompt_template, input_variables=['state.order_id', 'state.payment_id', 'state.sop_id', 'state.purchase_id', 'state.ticket_id'])

    agent_tool_msg_context = ''
    if len(state.used_tools_results):
        agent_tool_msg_context = "tool calling results:\n"
        for _msg in state.used_tools_results:
            # joined_json = "\n".join(json.dumps(msg.dict(), indent=2) for msg in _msg)
            joined_json = "\n".join(json.dumps({
                                        "content": msg.content,
                                        "name": msg.name,
                                        "status": msg.status,
                                        }, indent=2) for msg in _msg)
            agent_tool_msg_context += joined_json

    if state.list_of_ordered_items:
        joined_json =json.dumps(state.list_of_ordered_items)
        list_of_ordrs = "All Items ordered by customer are:\n" + joined_json

        print('list_of_ordrs', list_of_ordrs)
    
    messages = [state.messages[0]] + \
           [HumanMessage(prompt_template)] + \
           [SystemMessage(instruction_template)]
    
    if agent_tool_msg_context == '':
        messages += [AIMessage('No tool is called yet!')]
    else:
        messages += [AIMessage(agent_tool_msg_context)]

    print('agent_tool_msg_context=', agent_tool_msg_context)
    # Add ordered items

    if state.list_of_ordered_items:
        messages += [AIMessage(list_of_ordrs)]

    

    if state.list_of_sops:
        print('state.list_of_sops', state.list_of_sops)
        joined_json = "\n".join(json.dumps(state.list_of_sops, indent=2))
        list_of_sops = "All Standard Operating Procedures are:\n" + joined_json
        messages += [AIMessage(list_of_sops)]

    
    response = graph.llm_with_tools.invoke(messages, graph.thread_config)

    react_response = ReactAIMessage(response.content)

    print('thought: ', react_response.thought)
    print('agent_response: ', react_response.agent_response)

    print('---------------------------------------------------------------------------------------------------')

    tool_calls = response.tool_calls

    if len(tool_calls):
        _calls = []
        for tool_call in tool_calls:
            # tool_call['type'] = 'tool'
            _calls.append([ToolCall(**tool_call)])
        
        return {'used_tools': _calls, }
    
    return {'messages': [HumanMessage(prompt_template), AIMessage(react_response.agent_response)]}

def check_agent_action(state):
    
    if len(state.used_tools) != len(state.used_tools_results) or state.messages[-1].content  =='' :
        return 'tool'
    else:
        return 'final'

    
def tool_calling_node(graph, state:CaseContextState):
    
    tool_results = list()
    return_values = dict()
    for tool_call in state.used_tools[-1]:
        
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args", {})
        tool_call_id = tool_call.get("id")

        for tool in graph.tools:
            if tool.name == tool_name:  # Match tool by name
                try:

                    print('**************************CALLED**************************',tool.name, tool_args)
                    if isinstance(tool, StructuredTool):
                        result = tool.invoke(tool_args)  # Pass dict directly
                    else:
                        result = tool(**tool_args)  # Fallback for raw functions
                    

                    if isinstance(result['used_tools_results']['tool_output'], dict):
                        return_values.update(result['used_tools_results']['tool_output'])

                    tool_results.append(ToolMessage(
                        content=str(result['used_tools_results']['tool_output']),
                        tool_call_id=str(tool_call_id),
                        name=tool_name,
                        status=str(result['used_tools_results']['status'])
                    ))

                except Exception as e:
                    print('in exception')
                    tool_results.append(
                        ToolMessage(
                            content=f"Error: {str(e)}",
                            tool_call_id=tool_call_id,
                            name=tool_name,
                            status="error"
                        )
                    )

    return_values.update({'used_tools_results': [tool_results]})
    return return_values