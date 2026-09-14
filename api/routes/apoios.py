from fastapi import APIRouter

from api.schemas import ApoioCreate, ApoioRecord
from database.repositories.apoios_repository import create_apoio


router = APIRouter(prefix="/apoios", tags=["apoios"])


@router.post("", response_model=ApoioRecord, status_code=201)
def create_apoio_route(payload: ApoioCreate) -> ApoioRecord:
    return create_apoio(payload)
