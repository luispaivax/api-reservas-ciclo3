from sqlalchemy.orm import Session

from app.models import Sala
from app.schemas import SalaCreate, SalaUpdate


def criar_sala(db: Session, dados: SalaCreate):
    sala = Sala(**dados.model_dump())

    db.add(sala)
    db.commit()
    db.refresh(sala)

    return sala


def listar_salas(db: Session):
    return db.query(Sala).filter(
        Sala.ativo == True
    ).all()


def buscar_sala(db: Session, sala_id: int):
    return db.query(Sala).filter(
        Sala.id == sala_id,
        Sala.ativo == True
    ).first()


def atualizar_sala(db: Session, sala: Sala, dados: SalaUpdate):
    alteracoes = dados.model_dump(exclude_unset=True)

    for campo, valor in alteracoes.items():
        setattr(sala, campo, valor)

    db.commit()
    db.refresh(sala)

    return sala


def excluir_sala(db: Session, sala: Sala):
    sala.ativo = False

    db.commit()