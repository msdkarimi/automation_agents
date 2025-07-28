import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import APIRouter, Request, Response
from controllers.payments_controllers import get_all_payments_controller
from models import Payment, PaymentSchema
from typing import List


payment_bp = APIRouter(prefix="/payments", tags=["orders"])

# @orders_bp.post("/add")
# def insert_new_ticket(ticket: NewTicket, req:Request, res:Response):
#     result = insert_new_ticket_controller(ticket)
#     return result

@payment_bp.get("/", response_model=List[PaymentSchema])
def get_all_tickets(req:Request, res:Response):
    result = get_all_payments_controller()
    return result


