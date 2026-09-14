from uuid import UUID

from fastapi import APIRouter, HTTPException

from api.schemas import ApoioAdminList, ApoioAdminRecord, RelatoModeration
from database.repositories.apoios_repository import list_apoios, update_relato_approval


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/apoios", response_model=ApoioAdminList)
def list_apoios_route(limit: int = 200) -> ApoioAdminList:
    return list_apoios(limit=limit)


@router.patch("/apoios/{apoio_id}/relato", response_model=ApoioAdminRecord)
def moderate_relato_route(apoio_id: UUID, payload: RelatoModeration) -> ApoioAdminRecord:
    record = update_relato_approval(str(apoio_id), payload.relato_aprovado)
    if record is None:
        raise HTTPException(status_code=404, detail="Relato não encontrado.")
    return record
