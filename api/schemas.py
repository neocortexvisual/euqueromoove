from typing import Literal
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


Participation = Literal["apoiar", "piloto", "embaixador"]


class ApoioCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    instituicao: str = Field(min_length=2, max_length=140)
    bairro: str = Field(min_length=2, max_length=100)
    turno: str = Field(min_length=1, max_length=40)
    curso: str = Field(min_length=2, max_length=120)
    participacao: list[Participation] = Field(min_length=1)
    contato_apoio: str | None = Field(default=None, max_length=40)
    contato_piloto: str | None = Field(default=None, max_length=40)
    contato_embaixador: str | None = Field(default=None, max_length=40)
    mensagem: str | None = Field(default=None, max_length=500)
    confirmou_piloto: bool
    confirmou_independencia: bool = True

    @field_validator(
        "nome",
        "instituicao",
        "bairro",
        "turno",
        "curso",
        "contato_apoio",
        "contato_piloto",
        "contato_embaixador",
        "mensagem",
        mode="before",
    )
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = str(value).strip()
        return normalized or None

    @model_validator(mode="after")
    def validate_conditional_fields(self) -> "ApoioCreate":
        if "apoiar" in self.participacao and not self.contato_apoio:
            raise ValueError("contato_apoio é obrigatório para quem só quer apoiar.")

        if "piloto" in self.participacao and not self.contato_piloto:
            raise ValueError("contato_piloto é obrigatório para quem quer testar o piloto.")

        if "embaixador" in self.participacao and not self.contato_embaixador:
            raise ValueError(
                "contato_embaixador é obrigatório para quem quer ser embaixador."
            )

        if not self.confirmou_piloto:
            raise ValueError("É necessário confirmar o apoio ao projeto-piloto.")

        return self


class ApoioResponse(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    status: Literal["ok"] = "ok"


class ApoioRecord(ApoioResponse):
    created_at: datetime


class ApoioAdminRecord(BaseModel):
    id: UUID
    nome: str
    instituicao: str
    bairro: str
    turno: str
    curso: str | None = None
    faixa_etaria: str | None = None
    participacao: list[Participation]
    contato_apoio: str | None = None
    contato_piloto: str | None = None
    contato_embaixador: str | None = None
    mensagem: str | None = None
    relato_aprovado: bool = False
    confirmou_piloto: bool
    confirmou_independencia: bool
    created_at: datetime


class ApoioAdminStats(BaseModel):
    total: int
    apoiar: int
    piloto: int
    embaixador: int
    mensagens: int
    relatos_aprovados: int


class ApoioAdminList(BaseModel):
    stats: ApoioAdminStats
    apoios: list[ApoioAdminRecord]


class RelatoModeration(BaseModel):
    relato_aprovado: bool


class PublicRelato(BaseModel):
    id: UUID
    mensagem: str
    bairro: str
    curso: str | None = None
    created_at: datetime
