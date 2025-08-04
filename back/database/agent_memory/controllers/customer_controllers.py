import os 
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import Customer, CustomerSchema
from dbcore import DBCore
from psycopg2 import OperationalError

def _get_credentilas():
    return ('msd', '12345', 'agent_memory')
    # return (os.environ.get('postgres_user'),
    #         os.environ.get('postgres_pass'),
    #         os.environ.get('postgres_db_name'))


__all__ = ['insert_new_sop_catalog_controller', 'get_all_sop_catalog_controller']

def insert_customer_controller(customer, verbose=False) -> int:
    """
    input args : 
    retruns status of completion
    """
    # print(_get_credentilas())
    try:
        with DBCore(*_get_credentilas()) as db:
            new_customer = Customer(**customer)  # Use the imported model
            db.session.add(new_customer)

        if verbose:
            print(f'new item= {customer} has been added')

        return 0
    
    except OperationalError as e:
        print('There is problem with stablishing connection to DB, controle the credentials/db_name!', str(e))
        return 1
    except Exception as e:
        print(f'A generic exceptin happend during the insertion of item = {customer}', e)
        return 2
