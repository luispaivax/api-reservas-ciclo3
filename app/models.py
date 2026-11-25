from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    admin = Column(Boolean, default=False, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)

    reservas = relationship(
        "Reserva", back_populates="usuario"
    )


class Sala(Base):
    __tablename__ = "salas"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(30), nullable=False)
    descricao = Column(String(255), nullable=True)
    capacidade = Column(Integer, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)

    reservas = relationship(
        "Reserva", back_populates="sala"
    )

    __table_args__ = (
        CheckConstraint("capacidade > 0"),
        CheckConstraint("tipo IN ('sala', 'laboratorio')"),
    )


class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True)

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False
    )

    sala_id = Column(
        Integer,
        ForeignKey("salas.id"),
        nullable=False
    )

    inicio = Column(DateTime, nullable=False)
    fim = Column(DateTime, nullable=False)

    status = Column(
        String(20),
        default="ativa",
        nullable=False
    )

    usuario = relationship(
        "Usuario", back_populates="reservas"
    )

    sala = relationship(
        "Sala", back_populates="reservas"
    )

    __table_args__ = (
        CheckConstraint("fim > inicio"),
        CheckConstraint("status IN ('ativa', 'cancelada')"),
        Index(
            "ix_reservas_sala_horario",
            "sala_id", "inicio", "fim"
        ),
    )
