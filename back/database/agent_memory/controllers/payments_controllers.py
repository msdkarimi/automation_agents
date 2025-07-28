import os 
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import PaymentSchema, Payment
from dbcore import DBCore
from psycopg2 import OperationalError

def _get_credentilas():
    return ('msd', '12345', 'agent_memory')
    # return (os.environ.get('postgres_user'),
    #         os.environ.get('postgres_pass'),
    #         os.environ.get('postgres_db_name'))


__all__ = ['insert_new_sop_catalog_controller', 'get_all_payments_controller']

def insert_new_payment_controller(payment, verbose=False) -> int:
    """
    input args : 
    retruns status of completion
    """
    # print(_get_credentilas())
    try:
        with DBCore(*_get_credentilas()) as db:
            new_item = Payment(**payment)  # Use the imported model
            db.session.add(new_item)

        if verbose:
            print(f'new item= {payment} has been added')

        return 0
    
    except OperationalError as e:
        print('There is problem with stablishing connection to DB, controle the credentials/db_name!', str(e))
        return 1
    except Exception as e:
        print(f'A generic exceptin happend during the insertion of item = {payment}', e)
        return 2
    

def get_all_payments_controller(verbose=False):
    """
    Returns all rows from the Ticket table.
    """
    try:
        with DBCore(*_get_credentilas()) as db:
            payments = db.session.query(Payment).all()
            pydantic_tickets = [PaymentSchema.from_orm(payment) for payment in payments]
        
        if verbose:
            print(f"Retrieved {len(pydantic_tickets)} tickets")

        return pydantic_tickets

    except OperationalError as e:
        print('Problem with DB connection! Check credentials or DB name.', str(e))
        return []
    except Exception as e:
        print('An error occurred while fetching tickets:', e)
        return []
    

def get_payment_by_customer_order_purchase_controller(customer_id: str, order_id:str, purchase_id, verbose=False):
    """
    Returns all Payments for a specified customer_id and item_id and purchase_id.
    """
    try:
        with DBCore(*_get_credentilas()) as db:
            payment = db.session.query(Payment).filter(Payment.customer_id == customer_id and Payment.order_id == order_id and Payment.purchase_id == purchase_id ).first()
            if not payment:
                if verbose:
                    print(f"there is no purchase for customer_id={customer_id} and order_id={order_id}, and purchase_id={purchase_id}")
                return 0
            
            pydantic_payment = PaymentSchema.from_orm(payment) 
        
        if verbose:
            print(f"Retrieved {pydantic_payment} payment for customer_id = {customer_id} and order_id = {order_id} and purchase_id={purchase_id}")

        return pydantic_payment

    except OperationalError as e:
        print('Problem with DB connection! Check credentials or DB name.', str(e))
        return -1
    except Exception as e:
        print(f'Error while fetching orders for customer_id={customer_id}, order_id={order_id}, purchase_id={purchase_id}:', e)
        return -2


