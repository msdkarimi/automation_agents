import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from langchain_core.tools import tool
from agent_memory.controllers.ticket_links_controllers import get_ticket_link_by_id_controller, insert_new_ticket_linke_controller
from agent_memory.controllers.orders_catalog_controllers import get_orders_by_customer_id_controller
from agent_memory.controllers.purchase_controllers import get_purchase_by_customer_item_controller
from agent_memory.controllers.payments_controllers import get_payment_by_customer_order_purchase_controller
from agent_memory.controllers.sop_catalog_controllers import get_all_sop_catalog_controller
from state import CaseContextState
from langchain_core.messages import AIMessage
import re

class ReactAIMessage(AIMessage):
    @property
    def agent_response(self) -> str:
        # Remove the <think>...</think> block, return final answer
        return re.sub(r"<think>.*?</think>", "", self.content, flags=re.DOTALL).strip()

    @property
    def thought(self) -> str:
        # Extract <think>...</think> content
        match = re.search(r"<think>(.*?)</think>", self.content, flags=re.DOTALL)
        return match.group(1).strip() if match else ""
    



@tool
def get_ticket_details(ticket_id: int) -> CaseContextState:
    """this function is used to see if any link is created to given ticket_id or not.
    Args:
        ticket_id (int)
    Returns:
        In case of success, it returns keys related to the state of given link to ticket which is compatible with CaseContextState type.
        In case of failure it provides the reasoning. 
    """
    # Replace with actual database query

    print('tool is called!!')
    response = get_ticket_link_by_id_controller(ticket_id=ticket_id)
    if isinstance(response, int):
        if response >= 0:
            return {'used_tools_results': {'status': 'error', 'tool_output': {'id':response}}}
        else:
            return {'used_tools_results': {'status': 'error'}}
    else:
        _content = {'ticket_id':response.ticket_id,
                    'sop_id':response.sop_id,
                    'purchase_id':response.purchase_id,
                    'order_id':response.order_id,
                    'payment_id':response.payment_id,
                    'link_id': response.id
                    }
        return {'used_tools_results': {'status': 'success', 'tool_output': _content }}

@tool
def create_link_for_ticket(ticket_id: int, verbose=False) -> dict:
    """
    Inserts a new row into the link table for the given `ticket_id`, if it does not already exist.

    This function checks whether the specified `ticket_id` is present in the link table.
    If it is not found, a new entry is inserted to establish the necessary link.
    """

    if verbose:
        print('create_link_for_ticket tool is called!')

    response = insert_new_ticket_linke_controller(ticket_id=ticket_id)

    if response == 0:
        return {'used_tools_results': {'status': 'success', 'tool_output': f'link for the ticket_id={ticket_id} is inserted' }}
    else:
        return {'used_tools_results': {'status': 'error'}}

@tool
def get_customer_orders(customer_id:str):
    """this tool helps to find list of all orders of a given customer, based on this you can get more details of the order. below is an example of retrieved item from database:
    [
    order_id = Column(String, unique=True, nullable=False)
    customer_id = Column(String,ForeignKey("customers.customer_id"), nullable=True)
    purchase_id = Column(String, ForeignKey("purchases.purchase_id"), nullable=True)
    purchased_item_id = Column(String, ForeignKey("items.item_id"), nullable=True)
    order_number = Column(String, nullable=True)
    order_status = Column(String, nullable=False)
    order_date = Column(String, nullable=False)
    item_price = Column(Integer, nullable=False)
    ...]

    if you need the information related to order, 
    """
    respons = get_orders_by_customer_id_controller(customer_id)

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

    print('orders are', _ordered_items)

    return {'used_tools_results': {'status': 'success', 'tool_output': {'list_of_ordered_items':_ordered_items }}}

@tool
def set_ordered_item_based_on_item_id(item_info:dict):
    """    
        If item_info is available in the context and is not None, the agent should utilize the values from this dictionary.
        item_info is a dictionary containing information related to a purchased or ordered item.
    """
    item_id = item_info.pop('item_id', None)
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
    This tool retrieves information related to a payment.

    It should be used when payment details are needed in the workflow. To use this tool, 
    the following identifiers are required:
    - `customer_id`
    - `order_id`
    - `purchase_id`
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
    Retrieves all Standard Operating Procedures (SOPs) available in the system.

    This function is intended to fetch and return information related to all SOPs.
    It does not perform any filtering or selection.

    Later in the workflow, based on user input or comments, a specific SOP from 
    this list may be selected and linked to a ticket.

    Returns:
        dictionary : A dictionary of all available SOPs, each containing relevant metadata.
        e.g, "sop_id":"sop_title"
    """

    sops = get_all_sop_catalog_controller()
    
    _content = dict()

    for sop in sops:
        _content.update({"sopid": sop.sopid, "title": sop.title})

    return {'used_tools_results': {'status': 'success', 'tool_output': {'list_of_sops' :_content }}}  


@tool
def update_sop_state(sop_id, sop_tile):
    """
    Updates the ticket state with information about Standard Operating Procedures (SOPs) .
    This function should be called only when the 'list_of_sop' field 
    exists. sop_id and sop_tile are extracted from 
    the list and are used to update the current state of the agent).
    """

    return {'used_tools_results': {'status': 'success', 'tool_output': 
                                {'sop_id': sop_id, 'sop': {'title': sop_tile}}}}


def get_all_tools():
    return[
        get_ticket_details,
        create_link_for_ticket,
        get_customer_orders,
        set_ordered_item_based_on_item_id,
        get_purchase_by_customerId_itemId,
        get_payment_by_customer_order_purchase,
        get_list_of_sop_catalogs,
        update_sop_state,
    ]
