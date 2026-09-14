from datetime import UTC, datetime
import json
from uuid import uuid4

from api.schemas import (
    ApoioAdminList,
    ApoioAdminRecord,
    ApoioAdminStats,
    ApoioCreate,
    ApoioRecord,
    PublicRelato,
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
                curso,
                participacao,
                contato_apoio,
                contato_piloto,
                contato_embaixador,
                mensagem,
                relato_aprovado,
                confirmou_piloto,
                confirmou_independencia,
                created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, FALSE, %s, %s, %s)
            """,
            (
                apoio_id,
                payload.nome,
                payload.instituicao,
                payload.bairro,
                payload.turno,
                payload.curso,
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
                curso,
                faixa_etaria,
                participacao,
                contato_apoio,
                contato_piloto,
                contato_embaixador,
                mensagem,
                relato_aprovado,
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
            curso=row[5],
            faixa_etaria=row[6],
            participacao=json.loads(row[7]) if isinstance(row[7], str) else row[7],
            contato_apoio=row[8],
            contato_piloto=row[9],
            contato_embaixador=row[10],
            mensagem=row[11],
            relato_aprovado=row[12],
            confirmou_piloto=row[13],
            confirmou_independencia=row[14],
            created_at=row[15],
        )
        for row in rows
    ]

    stats = ApoioAdminStats(
        total=len(apoios),
        apoiar=sum("apoiar" in apoio.participacao for apoio in apoios),
        piloto=sum("piloto" in apoio.participacao for apoio in apoios),
        embaixador=sum("embaixador" in apoio.participacao for apoio in apoios),
        mensagens=sum(bool(apoio.mensagem) for apoio in apoios),
        relatos_aprovados=sum(apoio.relato_aprovado for apoio in apoios),
    )

    return ApoioAdminList(stats=stats, apoios=apoios)


def update_relato_approval(apoio_id: str, relato_aprovado: bool) -> ApoioAdminRecord | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            UPDATE apoios
            SET relato_aprovado = %s
            WHERE id = %s AND mensagem IS NOT NULL AND btrim(mensagem) <> ''
            RETURNING
                id,
                nome,
                instituicao,
                bairro,
                turno,
                curso,
                faixa_etaria,
                participacao,
                contato_apoio,
                contato_piloto,
                contato_embaixador,
                mensagem,
                relato_aprovado,
                confirmou_piloto,
                confirmou_independencia,
                created_at
            """,
            (relato_aprovado, apoio_id),
        ).fetchone()

    if row is None:
        return None

    return ApoioAdminRecord(
        id=row[0],
        nome=row[1],
        instituicao=row[2],
        bairro=row[3],
        turno=row[4],
        curso=row[5],
        faixa_etaria=row[6],
        participacao=json.loads(row[7]) if isinstance(row[7], str) else row[7],
        contato_apoio=row[8],
        contato_piloto=row[9],
        contato_embaixador=row[10],
        mensagem=row[11],
        relato_aprovado=row[12],
        confirmou_piloto=row[13],
        confirmou_independencia=row[14],
        created_at=row[15],
    )


def list_approved_relatos(limit: int = 8) -> list[PublicRelato]:
    safe_limit = min(max(limit, 1), 20)

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, mensagem, bairro, curso, created_at
            FROM apoios
            WHERE relato_aprovado = TRUE
              AND mensagem IS NOT NULL
              AND btrim(mensagem) <> ''
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (safe_limit,),
        ).fetchall()

    return [
        PublicRelato(
            id=row[0],
            mensagem=row[1],
            bairro=row[2],
            curso=row[3],
            created_at=row[4],
        )
        for row in rows
    ]
