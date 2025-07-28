import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import APIRouter, Request, Response
from controllers.purchase_controllers import insert_new_purchase_controller
from models import PurchaseSchema


purchases_bp = APIRouter(prefix="/purchases", tags=["purchases"])

@purchases_bp.post("/add")
def insert_new_item(item: PurchaseSchema, req:Request, res:Response):
    res = insert_new_purchase_controller(item)
    return res

