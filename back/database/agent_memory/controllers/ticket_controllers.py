import os 
from models import Ticket, TicketSchema
from dbcore import DBCore
from psycopg2 import OperationalError

def _get_credentilas():
    return ('msd', '12345', 'agent_memory')
    # return (os.environ.get('postgres_user'),
    #         os.environ.get('postgres_pass'),
    #         os.environ.get('postgres_db_name'))


__all__ = ['insert_new_ticket_controller']

def insert_new_ticket_controller(ticket, verbose=True) -> int:
    """
    input args : 
    retruns status of completion
    """
    # print(_get_credentilas())
    try:
        with DBCore(*_get_credentilas()) as db:
            new_purchase = Ticket(**ticket)  # Use the imported model
            db.session.add(new_purchase)

        if verbose:
            print(f'new purchase= {ticket} has been added')

        return 0
    
    except OperationalError as e:
        print('There is problem with stablishing connection to DB, controle the credentials/db_name!', str(e))
        return 1
    except Exception as e:
        print(f'A generic exceptin happend during the insertion of item = {ticket}', e)
        return 2


def get_all_tickets_controller(verbose=True):
    """
    Returns all rows from the Ticket table.
    """
    try:
        with DBCore(*_get_credentilas()) as db:
            tickets = db.session.query(Ticket).all()
            pydantic_tickets = [TicketSchema.from_orm(ticket) for ticket in tickets]
        
        if verbose:
            print(f"Retrieved {len(tickets)} tickets")

        return pydantic_tickets

    except OperationalError as e:
        print('Problem with DB connection! Check credentials or DB name.', str(e))
        return []
    except Exception as e:
        print('An error occurred while fetching tickets:', e)
        return []

