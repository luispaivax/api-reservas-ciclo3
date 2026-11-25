from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator
)
FUSO_BRASIL = ZoneInfo("America/Sao_Paulo")

class UsuarioCreate(BaseModel):

    nome: str = Field(min_length=3, max_length=100)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)

    model_config = ConfigDict(extra="forbid")

    @field_validator("nome", mode="before")
    @classmethod
    def validar_nome(cls, valor):
        if isinstance(valor, str):
            valor = valor.strip()

        return valor

    @field_validator("email", mode="before")
    @classmethod
    def normalizar_email(cls, valor):
        if isinstance(valor, str):
            return valor.strip().lower()

        return valor

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, valor):
        if not valor.strip():
            raise ValueError("A senha não pode ficar vazia.")

        return valor


class UsuarioLogin(BaseModel):

    email: EmailStr
    senha: str = Field(min_length=1, max_length=128)


class UsuarioResponse(BaseModel):

    id: int
    nome: str
    email: EmailStr
    admin: bool
    ativo: bool

    model_config = ConfigDict(from_attributes=True)

class SalaCreate(BaseModel):

    nome: str = Field(min_length=2, max_length=100)
    tipo: Literal["sala", "laboratorio"]
    descricao: str | None = Field(default=None, max_length=255)
    capacidade: int = Field(gt=0)

    model_config = ConfigDict(extra="forbid")

    @field_validator("nome", mode="before")
    @classmethod
    def validar_nome(cls, valor):
        if isinstance(valor, str):
            valor = valor.strip()

        return valor


class SalaUpdate(BaseModel):

    nome: str | None = Field(default=None, min_length=2, max_length=100)
    tipo: Literal["sala", "laboratorio"] | None = None
    descricao: str | None = Field(default=None, max_length=255)
    capacidade: int | None = Field(default=None, gt=0)
    ativo: bool | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("nome", mode="before")
    @classmethod
    def validar_nome(cls, valor):
        if isinstance(valor, str):
            valor = valor.strip()

        return valor


class SalaResponse(BaseModel):

    id: int
    nome: str
    tipo: str
    descricao: str | None
    capacidade: int
    ativo: bool

    model_config = ConfigDict(from_attributes=True)


class ReservaCreate(BaseModel):

    sala_id: int = Field(gt=0)
    inicio: datetime
    fim: datetime

    model_config = ConfigDict(extra="forbid")

    @field_validator("inicio", "fim")
    @classmethod
    def normalizar_data(cls, valor):

        if valor.tzinfo is not None:
            valor = valor.astimezone(
                FUSO_BRASIL
            ).replace(tzinfo=None)

        return valor

    @model_validator(mode="after")
    def validar_periodo(self):

        agora = datetime.now(
            FUSO_BRASIL
        ).replace(tzinfo=None)

        if self.fim <= self.inicio:
            raise ValueError(
                "O horário final deve ser posterior ao inicial."
            )

        if self.inicio <= agora:
            raise ValueError(
                "Não é permitido realizar reservas em datas passadas."
            )

        return self


class ReservaResponse(BaseModel):

    id: int
    usuario_id: int
    sala_id: int
    inicio: datetime
    fim: datetime
    status: Literal["ativa", "cancelada"]

    model_config = ConfigDict(from_attributes=True)