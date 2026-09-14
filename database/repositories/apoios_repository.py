from datetime import UTC, datetime
import json
from uuid import uuid4

from api.schemas import ApoioCreate, ApoioRecord
from database.connection import get_connection


def create_apoio(payload: ApoioCreate) -> ApoioRecord:
    apoio_id = uuid4()
    created_at = datetime.now(UTC)

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO apoios (
                id,
                nome,
                instituicao,
                bairro,
                turno,
                faixa_etaria,
                participacao,
                contato_apoio,
                contato_piloto,
                contato_embaixador,
                mensagem,
                confirmou_piloto,
                confirmou_independencia,
                created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                apoio_id,
                payload.nome,
                payload.instituicao,
                payload.bairro,
                payload.turno,
                payload.faixa_etaria,
                json.dumps(payload.participacao, ensure_ascii=False),
                payload.contato_apoio,
                payload.contato_piloto,
                payload.contato_embaixador,
                payload.mensagem,
                payload.confirmou_piloto,
                payload.confirmou_independencia,
                created_at,
            ),
        )

    return ApoioRecord(id=apoio_id, status="ok", created_at=created_at)
