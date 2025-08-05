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

def insert_new_ticket_linke_controller(ticket_id, verbose=True) -> int:
    """
    input args : 
    retruns status of completion
    """
    # print(_get_credentilas())
    print('inside insert_new_ticket_linke_controller', ticket_id)
    try:
        with DBCore(*_get_credentilas()) as db:
            new_t_l = TicketLink(**{'ticket_id':ticket_id})  # Use the imported model
            db.session.add(new_t_l)


        if verbose:
            print(f'new ticket link= {ticket_id} has been added')

        return 0
    
    except OperationalError as e:
        print('There is problem with stablishing connection to DB, controle the credentials/db_name!', str(e))
        return -1
    except Exception as e:
        print(f'A generic exceptin happend during the insertion of ticket link for ticket_id={ticket_id}', e)
        return -2



def update_ticket_link_controller(ticket_id: int, sop_id: str = None, purchase_id: str = None, order_id: str = None, payment_id: str = None, verbose=True) -> int:
    try:
        with DBCore(*_get_credentilas()) as db:
            # Query the existing ticket link
            ticket_link = db.session.query(TicketLink).filter_by(ticket_id=ticket_id).first()

            if not ticket_link:
                print(f"No ticket link found with ticket_id={ticket_id}")
                return -3

            if sop_id is not None:
                ticket_link.sop_id = sop_id
            if purchase_id is not None:
                ticket_link.purchase_id = purchase_id
            if order_id is not None:
                ticket_link.order_id = order_id
            if payment_id is not None:
                ticket_link.payment_id = payment_id

            if verbose:
                print(f"Ticket link for ticket_id={ticket_id} has been updated.")

            return 0

    except OperationalError as e:
        print('There is a problem with establishing a connection to the DB. Check credentials/db_name!', str(e))
        return -1
    except Exception as e:
        print(f"A generic exception occurred during the update of ticket link for ticket_id={ticket_id}", e)
        return -2



async def get_ticket_link_by_id_controller(ticket_id, verbose=True):
    """
    Return link to ticket by id
    """
    try:
        with DBCore(*_get_credentilas()) as db:
            ticket = db.session.query(TicketLink).filter_by(ticket_id=ticket_id).first()
            if not ticket:
                if verbose:
                    print(f"there is no link to ticket with id={ticket_id}")
                return 0

            pydantic_ticket = TicketLinkSchema.from_orm(ticket)
        
        if verbose:
            print('jef', f"Retrieved ticket with ID {ticket_id}")
        
        return pydantic_ticket

    except OperationalError as e:
        print('jef','Problem with DB connection! Check credentials or DB name.', str(e))
        return -1
    except Exception as e:
        print('jef', 'An error occurred while fetching the ticket:', e)
        return -2


