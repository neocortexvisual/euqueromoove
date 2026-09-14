from fastapi import APIRouter

from api.schemas import ApoioAdminList
from database.repositories.apoios_repository import list_apoios


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/apoios", response_model=ApoioAdminList)
def list_apoios_route(limit: int = 200) -> ApoioAdminList:
    return list_apoios(limit=limit)
