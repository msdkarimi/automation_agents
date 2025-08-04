import os 
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import SOPCatalog, SOPCatalogSchema
from dbcore import DBCore
from psycopg2 import OperationalError

def _get_credentilas():
    return ('msd', '12345', 'agent_memory')
    # return (os.environ.get('postgres_user'),
    #         os.environ.get('postgres_pass'),
    #         os.environ.get('postgres_db_name'))


__all__ = ['insert_new_sop_catalog_controller', 'get_all_sop_catalog_controller']

def insert_new_sop_catalog_controller(sop_cat, verbose=False) -> int:
    """
    input args : 
    retruns status of completion
    """
    # print(_get_credentilas())
    try:
        with DBCore(*_get_credentilas()) as db:
            new_item = SOPCatalog(**sop_cat)  # Use the imported model
            db.session.add(new_item)

        if verbose:
            print(f'new item= {sop_cat} has been added')

        return 0
    
    except OperationalError as e:
        print('There is problem with stablishing connection to DB, controle the credentials/db_name!', str(e))
        return 1
    except Exception as e:
        print(f'A generic exceptin happend during the insertion of item = {sop_cat}', e)
        return 2
    

def get_all_sop_catalog_controller(verbose=False):
    """
    Returns all rows from the Ticket table.
    """
    try:
        with DBCore(*_get_credentilas()) as db:
            tickets = db.session.query(SOPCatalog).all()
            pydantic_tickets = [SOPCatalogSchema.from_orm(ticket) for ticket in tickets]
        
        if verbose:
            print(f"Retrieved {len(tickets)} Sops")

        return pydantic_tickets

    except OperationalError as e:
        print('Problem with DB connection! Check credentials or DB name.', str(e))
        return []
    except Exception as e:
        print('An error occurred while fetching tickets:', e)
        return []
