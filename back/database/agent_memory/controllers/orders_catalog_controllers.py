import os 
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import Orders, OrdersSchema
from dbcore import DBCore
from psycopg2 import OperationalError

def _get_credentilas():
    return ('msd', '12345', 'agent_memory')
    # return (os.environ.get('postgres_user'),
    #         os.environ.get('postgres_pass'),
    #         os.environ.get('postgres_db_name'))


__all__ = ['insert_new_sop_catalog_controller', 'get_all_sop_catalog_controller']

def insert_new_order_controller(order, verbose=False) -> int:
    """
    input args : 
    retruns status of completion
    """
    # print(_get_credentilas())
    try:
        with DBCore(*_get_credentilas()) as db:
            new_item = Orders(**order)  # Use the imported model
            db.session.add(new_item)

        if verbose:
            print(f'new item= {order} has been added')

        return 0
    
    except OperationalError as e:
        print('There is problem with stablishing connection to DB, controle the credentials/db_name!', str(e))
        return 1
    except Exception as e:
        print(f'A generic exceptin happend during the insertion of item = {order}', e)
        return 2
    

def get_all_orders_controller(verbose=True):
    """
    Returns all rows from the Ticket table.
    """
    try:
        with DBCore(*_get_credentilas()) as db:
            tickets = db.session.query(Orders).all()
            pydantic_tickets = [OrdersSchema.from_orm(ticket) for ticket in tickets]
        
        if verbose:
            print(f"Retrieved {len(tickets)} tickets")

        return pydantic_tickets

    except OperationalError as e:
        print('Problem with DB connection! Check credentials or DB name.', str(e))
        return []
    except Exception as e:
        print('An error occurred while fetching tickets:', e)
        return []


def get_orders_by_customer_id_controller(customer_id: str, verbose=False):
    """
    Returns all Orders for a specific customer_id.
    """
    try:
        with DBCore(*_get_credentilas()) as db:
            tickets = db.session.query(Orders).filter(Orders.customer_id == customer_id).all()
            pydantic_orders = [OrdersSchema.from_orm(ticket) for ticket in tickets]
        
        if verbose:
            print(f"Retrieved {len(pydantic_orders)} tickets for customer_id = {customer_id}")

        return pydantic_orders

    except OperationalError as e:
        print('Problem with DB connection! Check credentials or DB name.', str(e))
        return -1
    except Exception as e:
        print(f'Error while fetching orders for customer_id={customer_id}:', e)
        return -2


