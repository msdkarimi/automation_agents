import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import APIRouter, Request, Response
from controllers.ticket_controllers import insert_new_ticket_controller, get_all_tickets_controller
from models import NewTicket, TicketSchema
from typing import List


tickets_bp = APIRouter(prefix="/tickets", tags=["tickets"])

@tickets_bp.post("/add")
def insert_new_ticket(ticket: NewTicket, req:Request, res:Response):
    result = insert_new_ticket_controller(ticket)
    return result

@tickets_bp.get("/", response_model=List[TicketSchema])
async def get_all_tickets(req:Request, res:Response):
    result = await get_all_tickets_controller()
    print('all tickets are retirvied')
    return result


