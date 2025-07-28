import os 
from models import Purchase, PurchaseSchema
from dbcore import DBCore
from psycopg2 import OperationalError

def _get_credentilas():
    return ('msd', '12345', 'agent_memory')
    # return (os.environ.get('postgres_user'),
    #         os.environ.get('postgres_pass'),
    #         os.environ.get('postgres_db_name'))


__all__ = ['insert_new_purchase_controller']

def insert_new_purchase_controller(purchase, verbose=True) -> int:
    """
    input args : 
    retruns status of completion
    """
    # print(_get_credentilas())
    try:
        with DBCore(*_get_credentilas()) as db:
            new_purchase = Purchase(**purchase.dict())  # Use the imported model
            db.session.add(new_purchase)

        if verbose:
            print(f'new purchase= {purchase} has been added')

        return 0
    
    except OperationalError as e:
        print('There is problem with stablishing connection to DB, controle the credentials/db_name!', str(e))
        return 1
    except Exception as e:
        print(f'A generic exceptin happend during the insertion of item = {purchase}', e)
        return 2
    

def get_purchase_by_customer_item_controller(customer_id: str, item_id:str, verbose=False):
    """
    Returns all Purchases for a specific customer_id and item_id.
    """
    try:
        with DBCore(*_get_credentilas()) as db:
            purchase = db.session.query(Purchase).filter(Purchase.customer_id == customer_id and Purchase.purchased_item_id == item_id ).first()
            if not purchase:
                if verbose:
                    print(f"there is no purchase for customer_id={customer_id} and item_id={item_id}")
                return 0
            
            pydantic_purchases = PurchaseSchema.from_orm(purchase) 
        
        if verbose:
            print(f"Retrieved {len(pydantic_purchases)} purchase for customer_id = {customer_id} and item_id = {item_id}")

        return pydantic_purchases

    except OperationalError as e:
        print('Problem with DB connection! Check credentials or DB name.', str(e))
        return -1
    except Exception as e:
        print(f'Error while fetching orders for customer_id={customer_id}, item_id={item_id}:', e)
        return -2

