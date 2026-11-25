
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.schemas import SalaCreate, SalaUpdate, SalaResponse
from app.services import sala as sala_service

router = APIRouter(prefix="/salas",tags=["Salas"])

@router.post("/", response_model=SalaResponse,status_code=status.HTTP_201_CREATED)
def criar_sala(dados: SalaCreate, db: Session = Depends(get_db)):
    return sala_service.criar_sala(db, dados)

@router.get("/", response_model=list[SalaResponse])
def listar_salas(db: Session = Depends(get_db)):
    return sala_service.listar_salas(db)

@router.get("/{sala_id}", response_model=SalaResponse)
def buscar_sala(sala_id: int, db: Session = Depends(get_db)):
    sala = sala_service.buscar_sala(db, sala_id)

    if sala is None:
        raise HTTPException(
            status_code=404,
            detail="Sala não encontrada."
        )

    return sala

@router.patch("/{sala_id}", response_model=SalaResponse)
def atualizar_sala(
    sala_id: int,
    dados: SalaUpdate,
    db: Session = Depends(get_db)
):
    sala = sala_service.buscar_sala(db, sala_id)

    if sala is None:
        raise HTTPException(
            status_code=404,
            detail="Sala não encontrada."
        )

    try:
        return sala_service.atualizar_sala(db, sala, dados)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Dados inválidos para atualização da sala."
        )

@router.delete("/{sala_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_sala(sala_id: int, db: Session = Depends(get_db)):
    sala = sala_service.buscar_sala(db, sala_id)

    if sala is None:
        raise HTTPException(
            status_code=404,
            detail="Sala não encontrada."
        )

    sala_service.excluir_sala(db, sala)
