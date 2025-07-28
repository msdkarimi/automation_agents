import os 

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', )))

from models import TicketLink, TicketLinkSchema
from dbcore import DBCore
from psycopg2 import OperationalError



def _get_credentilas():
    return ('msd', '12345', 'agent_memory')
    # return (os.environ.get('postgres_user'),
    #         os.environ.get('postgres_pass'),
    #         os.environ.get('postgres_db_name'))


__all__ = ['insert_new_ticket_linke_controller']

def insert_new_ticket_linke_controller(ticket_id, verbose=False) -> int:
    """
    input args : 
    retruns status of completion
    """
    # print(_get_credentilas())
    try:
        with DBCore(*_get_credentilas()) as db:
            new_t_l = TicketLink(**ticket_id)  # Use the imported model
            db.session.add(new_t_l)
            db.session.flush()
            inserted_id = new_t_l.id 

        if verbose:
            print(f'new ticket link= {ticket_id} has been added')

        return inserted_id
    
    except OperationalError as e:
        print('There is problem with stablishing connection to DB, controle the credentials/db_name!', str(e))
        return -1
    except Exception as e:
        print(f'A generic exceptin happend during the insertion of item = {ticket_id}', e)
        return -2


def get_ticket_link_by_id_controller(ticket_id, verbose=False):
    """
    Return link to ticket by id
    """
    try:
        with DBCore(*_get_credentilas()) as db:
            ticket = db.session.query(TicketLink).filter_by(id=ticket_id).first()
            if not ticket:
                if verbose:
                    print(f"there is no link to ticket with id={ticket_id}")
                return 0

            pydantic_ticket = TicketLinkSchema.from_orm(ticket)
        
        if verbose:
            print(f"Retrieved ticket with ID {ticket_id}")
        
        return pydantic_ticket

    except OperationalError as e:
        print('Problem with DB connection! Check credentials or DB name.', str(e))
        return -1
    except Exception as e:
        print('An error occurred while fetching the ticket:', e)
        return -2


