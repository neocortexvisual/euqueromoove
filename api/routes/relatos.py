from fastapi import APIRouter

from api.schemas import PublicRelato
from database.repositories.apoios_repository import list_approved_relatos


router = APIRouter(prefix="/relatos", tags=["relatos"])


@router.get("", response_model=list[PublicRelato])
def list_public_relatos_route(limit: int = 8) -> list[PublicRelato]:
    return list_approved_relatos(limit=limit)
