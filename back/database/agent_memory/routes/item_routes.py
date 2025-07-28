import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import APIRouter, Request, Response
from controllers.item_controllers import insert_new_item_controller
from models import ItemSchema


item_bp = APIRouter(prefix="/items", tags=["items"])


@item_bp.post("/add")
def insert_new_item(item: ItemSchema, req:Request, res:Response):
    print('in func!!!')

    res = insert_new_item_controller(item)
    return res

