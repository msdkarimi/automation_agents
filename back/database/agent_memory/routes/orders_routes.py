import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import APIRouter, Request, Response
from controllers.orders_catalog_controllers import get_all_orders_controller
from models import Orders, OrdersSchema
from typing import List


orders_bp = APIRouter(prefix="/orders", tags=["orders"])

# @orders_bp.post("/add")
# def insert_new_ticket(ticket: NewTicket, req:Request, res:Response):
#     result = insert_new_ticket_controller(ticket)
#     return result

@orders_bp.get("/", response_model=List[OrdersSchema])
def get_all_tickets(req:Request, res:Response):
    result = get_all_orders_controller()
    return result


