import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import APIRouter, Request, Response
from controllers.sop_catalog_controllers import get_all_sop_catalog_controller
from models import SOPCatalogSchema
from typing import List


sop_cats_bp = APIRouter(prefix="/sop_cats", tags=["sop_cats"])


@sop_cats_bp.get("/", response_model=List[SOPCatalogSchema])
def get_all_tickets(req:Request, res:Response):
    result = get_all_sop_catalog_controller()
    return result


