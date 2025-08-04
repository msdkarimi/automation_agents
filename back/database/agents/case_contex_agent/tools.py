import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from langchain_core.tools import tool
from agent_memory.controllers.ticket_links_controllers import get_ticket_link_by_id_controller, insert_new_ticket_linke_controller
from agent_memory.controllers.orders_catalog_controllers import get_orders_by_customer_id_controller
from agent_memory.controllers.purchase_controllers import get_purchase_by_customer_item_controller
from agent_memory.controllers.payments_controllers import get_payment_by_customer_order_purchase_controller
from agent_memory.controllers.sop_catalog_controllers import get_all_sop_catalog_controller
from case_contex_agent.state import CaseContextState
from langchain_core.messages import AIMessage
import re

# back\database\agents\case_contex_agent\tools.py

@tool
def get_ticket_details(ticket_id: int, ) -> CaseContextState:
    """this function is used to see if any link is created to given ticket_id or not.
    Args:
        ticket_id (int)
    Returns:
        In case of success, it returns keys related to the state of given link to ticket which is compatible with CaseContextState type.
        In case of failure it provides the reasoning. 
    """

    response = get_ticket_link_by_id_controller(ticket_id=ticket_id)
    if isinstance(response, int):
        if response > 0:
        #    'there is not any link associated to ticket_id={ticket_id}

            response = insert_new_ticket_linke_controller(ticket_id=ticket_id)

            if response == 0:
                return {'used_tools_results': {'status': 'success', 'tool_output': f'link for the ticket_id={ticket_id} is created' }}
            else:
                return {'used_tools_results': {'status': 'error'}}



        else:
            return 'there is problemt with connection to database, please check the database connection.'

    else:
        _content = {'ticket_id':response.ticket_id,
                    'link_id': response.id,
                    'sop_id': response.sop_id,
                    'purchase_id': response.purchase_id, 
                    'order_id': response.order_id,
                    'payment_id': response.payment_id
                    }

        return {'used_tools_results': {'status': 'success', 'tool_output': _content }}


@tool
def get_customer_all_orders(customer_id: str):
    """
    this tool is used to just give order history of given customer, this helps us to better understand which order is related to customer comment. 
    """
    print('called for customer=', customer_id)

    respons = get_orders_by_customer_id_controller(customer_id)

    if isinstance(respons, int):
        return {'used_tools_results': {'status': 'error'}}
    elif isinstance(respons, list) and len(respons)==0:
        return {'used_tools_results': {'status': 'success', 'tool_output': f'there is not any order associated to customer {customer_id}.'}}
    
    _ordered_items = dict()
    for order in respons:
        tmp = order.item.model_dump()
        tmp.pop('id', None)
        _ordered_items.update( {f'the order_id={order.order_id} and order_number={order.order_number} for item:' :tmp })
        # _ordered_items += f'ordered item id is {order.item.item_id}, ordered item name is: {order.item.item_name},and its description is {order.item.item_description}\n'


    return {'used_tools_results': {'status': 'success', 'tool_output': {'list_of_ordered_items':_ordered_items }}}
    
@tool
def update_item_state(item_id, item_info: dict):
    """
    Identifies and updates the relevant item from the user's order history based on references in their comment.

    This tool analyzes the user's comment to extract item-related cues (such as item name or description),
    matches them against the user's list of past orders, and selects the most relevant item.
    """
    item_info.pop('item_id', None)
    return {'used_tools_results': {'status': 'success', 'tool_output':
                                   {'item_id': item_id, 'order': item_info}}}

@tool
def get_purchase_by_customerId_itemId(customer_id:str, item_id:str):
    """
    This tool updates the purchase information in the application state.
    It should be used when both `customer_id` and `item_id` are available. Upon execution, 
    it will update the `purchase_id` and associated purchase details in the state.
    """



    purchase = get_purchase_by_customer_item_controller(customer_id=customer_id, item_id=item_id)

    if isinstance(purchase, int):
        if purchase<0:
            return {'used_tools_results': {'status': 'error'}}
        
        return {'used_tools_results': {'status': 'error', 'tool_output': f'there is not any purchase associated to customer {customer_id} for item with id ={item_id}.'}}

    purchase = purchase.dict()
    purchase.pop('customer', None)
    purchase.pop('item', None)
    purchase_id = purchase.pop('purchase_id', None)
    purchase.pop('id', None)
    purchase.pop('customer_id', None)
    purchase.pop('purchased_item_id', None)


    _content = {
        'purchase_id':purchase_id,
        'purchase':purchase,
                }
    return {'used_tools_results': {'status': 'success', 'tool_output': _content }}  



@tool
def get_payment_by_customer_order_purchase(customer_id:str, order_id:str, purchase_id:str):
    """
    Retrieves detailed payment information for a specific purchase within a customer's order.

    Use this tool to find details about a transaction, such as payment status,
    amount, method, or transaction ID. This is particularly useful for
    addressing customer inquiries about charges, refunds, or payment confirmation.
    """

    payment = get_payment_by_customer_order_purchase_controller(customer_id=customer_id, order_id=order_id, purchase_id=purchase_id)

    if isinstance(payment, int):
            if payment<0:
                return {'used_tools_results': {'status': 'error'}}
            
            return {'used_tools_results': {'status': 'error', 'tool_output': f'there is not any payment associated to customer {customer_id} for order with id={order_id} and purchase with id={purchase_id}.'}}

    
    payment = payment.dict()

    payment.pop('customer', None)
    payment.pop('item', None)
    payment.pop('customer_id', None)
    payment.pop('id', None)
    payment.pop('purchase_id', None)
    payment.pop('order_id', None)
    payment_id = payment.pop('payment_id', None)

    _content = {
        'payment_id':payment_id,
        'payment':payment,
            }
    return {'used_tools_results': {'status': 'success', 'tool_output': _content }}  

@tool
def get_list_of_sop_catalogs():
    """
    Retrieves the complete list of available Standard Operating Procedures (SOPs).

    Use this tool to get a full catalog of SOPs. The output can be used to
    identify and link a specific SOP to a customer issue or ticket based on
    the customer's request or details.
    """
    sops = get_all_sop_catalog_controller()
    
    _content = dict()

    for sop in sops:
        _content.update({sop.sopid:{"title": sop.title}})

    return {'used_tools_results': {'status': 'success', 'tool_output': {'list_of_sops' :_content }}}  


@tool
def update_sop_state(sop_id, sop_tile):
    """
    Selects and sets the current Standard Operating Procedure (SOP) for the conversation.

    This tool identifies the most relevant SOP from a list and updates the agent's
    state with its ID and title. It is crucial for focusing the conversation
    on the correct procedure to follow based on the customer's input.
    """

    return {'used_tools_results': {'status': 'success', 'tool_output': 
                                {'sop_id': sop_id, 'sop': {'title': sop_tile}}}}

@tool
def get_customer_orders(state: CaseContextState):
    """
    Retrieves a list of all orders for a specific customer.

    This tool is used to get a complete history of a customer's purchases.
    It returns a list of order records, each containing key details like order ID,
    status, date, and price. This information is a prerequisite for a more
    detailed analysis of individual orders.
    """

    respons = get_orders_by_customer_id_controller(state.customer_id)

    if isinstance(respons, int):
        return {'used_tools_results': {'status': 'error'}}
    elif isinstance(respons, list) and len(respons)==0:
        return {'used_tools_results': {'status': 'success', 'tool_output': f'there is not any order associated to customer {customer_id}.'}}
    
    _ordered_items = dict()
    for order in respons:
        tmp = order.item.model_dump()
        tmp.pop('id', None)
        _ordered_items.update( {order.order_id :tmp })
        # _ordered_items += f'ordered item id is {order.item.item_id}, ordered item name is: {order.item.item_name},and its description is {order.item.item_description}\n'


    # return {'list_of_ordered_items': _ordered_items}

    return {'used_tools_results': {'status': 'success', 'tool_output': {'list_of_ordered_items': _ordered_items }}}  


def get_all_tools():
    return[
        get_customer_all_orders,
        update_item_state,
        get_purchase_by_customerId_itemId,
        get_payment_by_customer_order_purchase,
        get_list_of_sop_catalogs,
        update_sop_state,
    ]
