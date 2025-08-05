import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from langchain_core.tools import tool
from agent_memory.controllers.ticket_links_controllers import get_ticket_link_by_id_controller, insert_new_ticket_linke_controller, update_ticket_link_controller
from agent_memory.controllers.orders_catalog_controllers import get_orders_by_customer_id_controller
from agent_memory.controllers.purchase_controllers import get_purchase_by_customer_item_controller
from agent_memory.controllers.payments_controllers import get_payment_by_customer_order_purchase_controller
from agent_memory.controllers.sop_catalog_controllers import get_all_sop_catalog_controller
from case_contex_agent.state import CaseContextState
from langchain_core.messages import AIMessage
import re

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
    """Retrieves the complete order history for a given customer.

    This tool fetches all orders and the items within them associated with a
    specific customer ID. It is typically the first step when a customer
    inquires about a past purchase. The returned list should be presented
    to the user so they can identify the specific item they are interested in.

    Args:
        customer_id (str): The unique identifier for the customer.

    Returns:
       A list of dictionaries, where each dictionary represents a
        single item from an order. Returns an empty list if the customer has
        no order history. Each dictionary has the following structure:
        {
            'order_id': str,          # The unique ID for the order
            'order_number': str,      # The human-readable order number
            'order_date': str,        # The date the order was placed
            'item_id': str,           # The unique ID for the item
            'item_name': str,         # The name of the item
            'item_description': str   # A brief description of the item
        }
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

    print(_ordered_items)

    return {'used_tools_results': {'status': 'success', 'tool_output': {'list_of_ordered_items':_ordered_items }}}
    
@tool
def update_item_orderId_state(item_id, order_id, item_info: dict):
    """
    Sets the context to a specific item within an order for subsequent actions.
    This tool "selects" or "focuses on" an item that the user has confirmed.
    It stores the item's details in the system's state, making them available for other tools. 
    This is a crucial step to perform before calling tools that act on a specific item, such as initiating a return, checking a warranty, or getting payment details.

    You should call this tool after the user has identified an item from their
    order history (e.g., retrieved using `get_customer_all_orders`).

    """
    item_info.pop('item_id', None)
    return {'used_tools_results': {'status': 'success', 'tool_output':
                                   {'item_id': item_id, 'order': item_info, 'order_id':order_id}}}


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
def update_sop_state(sop_id, sop_title):
    """
    Selects and sets a Standard Operating Procedure (SOP) for the conversation.

    This tool identifies the most relevant SOP from a list of SOPs and updates the agent's
    state with its ID and title. It is crucial for focusing the conversation
    on the correct procedure to follow based on the customer's input.
    """

    return {'used_tools_results': {'status': 'success', 'tool_output': 
                                {'sop_id': sop_id, 'sop': {'title': sop_title}}}}

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

    return {'used_tools_results': {'status': 'success', 'tool_output': {'list_of_ordered_items': _ordered_items }}}  

@tool
def update_linked_information_database(ticket_id:int, sop_id:str=None, purchase_id:str=None, order_id:str=None, payment_id:str=None):
    """Finalizes the ticket resolution process by saving all linked information to the database.

    This tool should be called as the very last step, after all relevant information—such as 
    Standard Operating Procedures (SOPs), purchase details, order specifics, and payment records—has 
    been identified. It takes the ticket ID and any available entity IDs and updates the ticket's 
    record in the database to create permanent links.

    Args:
        ticket_id (int): The unique identifier for the customer service ticket being updated.
        sop_id (str, optional): The ID of the Standard Operating Procedure (SOP). Defaults to None.
        purchase_id (str, optional): The ID of the customer's purchase. Defaults to None.
        order_id (str, optional): The ID of the specific order. Defaults to None.
        payment_id (str, optional): The ID of the payment transaction. Defaults to None.

    Returns:
        dict: A dictionary containing a structured result of the operation, which is optimal for the LLM.
    """
    respons = update_ticket_link_controller(ticket_id, sop_id, purchase_id, order_id, payment_id)

    # --- Updated Logic Starts Here ---

    if respons == 0:
        # Success case: Create a structured dictionary of what was linked.
        linked_data = {}
        if sop_id: linked_data['sop_id'] = sop_id
        if purchase_id: linked_data['purchase_id'] = purchase_id
        if order_id: linked_data['order_id'] = order_id
        if payment_id: linked_data['payment_id'] = payment_id

        # structured_output = {
        #     "message": f"Linked information for ticket with id= {ticket_id} has been successfully updated and saved into the database.",
        #     "ticket_id": ticket_id,
        #     "updated_links": linked_data
        # }
        return {'used_tools_results': {'status': 'success', 'tool_output':f"last tool call was successful, linked information for ticket with id= {ticket_id} has been successfully updated and saved into the database." }}
    else:
        # Error case: Report what the tool was trying to link.
        attempted_links = {
            "sop_id": sop_id,
            "purchase_id": purchase_id,
            "order_id": order_id,
            "payment_id": payment_id
        }
        # Filter out None values to show exactly what was attempted
        attempted_links = {k: v for k, v in attempted_links.items() if v is not None}

        error_output = {
            "message": f"An error occurred while attempting to update ticket {ticket_id}.",
            "ticket_id": ticket_id,
            "attempted_links": attempted_links
        }
        return {'used_tools_results': {'status': 'error', 'tool_output': error_output}}



def get_all_tools():
    return[
        get_customer_all_orders,
        update_item_orderId_state,
        get_purchase_by_customerId_itemId,
        get_payment_by_customer_order_purchase,
        get_list_of_sop_catalogs,
        update_sop_state,
        update_linked_information_database
    ]
