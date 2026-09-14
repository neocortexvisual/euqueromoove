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
    faixa_etaria: str = Field(min_length=1, max_length=40)
    participacao: list[Participation] = Field(min_length=1)
    contato_piloto: str | None = Field(default=None, max_length=40)
    contato_embaixador: str | None = Field(default=None, max_length=40)
    mensagem: str | None = Field(default=None, max_length=500)
    confirmou_piloto: bool
    confirmou_independencia: bool

    @field_validator(
        "nome",
        "instituicao",
        "bairro",
        "turno",
        "faixa_etaria",
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
        if "piloto" in self.participacao and not self.contato_piloto:
            raise ValueError("contato_piloto é obrigatório para quem quer testar o piloto.")

        if "embaixador" in self.participacao and not self.contato_embaixador:
            raise ValueError(
                "contato_embaixador é obrigatório para quem quer ser embaixador."
            )

        if not self.confirmou_piloto:
            raise ValueError("É necessário confirmar o apoio ao projeto-piloto.")

        if not self.confirmou_independencia:
            raise ValueError("É necessário confirmar a independência do movimento.")

        return self


class ApoioResponse(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    status: Literal["ok"] = "ok"


class ApoioRecord(ApoioResponse):
    created_at: datetime
