from datetime import UTC, datetime
import json
from uuid import uuid4

from api.schemas import (
    ApoioAdminList,
    ApoioAdminRecord,
    ApoioAdminStats,
    ApoioCreate,
    ApoioRecord,
)
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


def list_apoios(limit: int = 200) -> ApoioAdminList:
    safe_limit = min(max(limit, 1), 500)

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
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
            FROM apoios
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (safe_limit,),
        ).fetchall()

    apoios = [
        ApoioAdminRecord(
            id=row[0],
            nome=row[1],
            instituicao=row[2],
            bairro=row[3],
            turno=row[4],
            faixa_etaria=row[5],
            participacao=row[6],
            contato_apoio=row[7],
            contato_piloto=row[8],
            contato_embaixador=row[9],
            mensagem=row[10],
            confirmou_piloto=row[11],
            confirmou_independencia=row[12],
            created_at=row[13],
        )
        for row in rows
    ]

    stats = ApoioAdminStats(
        total=len(apoios),
        apoiar=sum("apoiar" in apoio.participacao for apoio in apoios),
        piloto=sum("piloto" in apoio.participacao for apoio in apoios),
        embaixador=sum("embaixador" in apoio.participacao for apoio in apoios),
        mensagens=sum(bool(apoio.mensagem) for apoio in apoios),
    )

    return ApoioAdminList(stats=stats, apoios=apoios)
