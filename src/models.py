from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Numeric
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Enum

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


class Usuario(Base):

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String(120), nullable=False)

    dni = Column(String(8), unique=True, nullable=False, index=True)

    tarjeta = Column(String(16), unique=True, nullable=False)

    password = Column(String(255), nullable=False)

    codigo_seguridad = Column(String(4), nullable=False)

    estado = Column(
        Enum("Verificado", "Pendiente", "Bloqueado", name="estado_usuario"),
        default="Verificado"
    )

    fecha_creacion = Column(DateTime, server_default=func.now())

    cuentas = relationship(
        "Cuenta",
        back_populates="usuario",
        cascade="all, delete"
    )

    creditos = relationship(
        "Credito",
        back_populates="usuario",
        cascade="all, delete"
    )

    transferencias = relationship(
        "Transferencia",
        back_populates="usuario",
        cascade="all, delete"
    )

    pagos = relationship(
        "Pago",
        back_populates="usuario",
        cascade="all, delete"
    )

    movimientos = relationship(
        "Movimiento",
        back_populates="usuario",
        cascade="all, delete"
    )


class Cuenta(Base):

    __tablename__ = "cuentas"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False
    )

    numero_cuenta = Column(
        String(20),
        unique=True,
        nullable=False
    )

    tipo_cuenta = Column(
        Enum("Cuenta de Ahorros", "Cuenta Corriente", name="tipo_cuenta"),
        default="Cuenta de Ahorros"
    )

    saldo = Column(
        Numeric(12, 2),
        default=0
    )

    estado = Column(
        Enum("Activa", "Bloqueada", name="estado_cuenta"),
        default="Activa"
    )

    fecha_creacion = Column(
        DateTime,
        server_default=func.now()
    )

    usuario = relationship(
        "Usuario",
        back_populates="cuentas"
    )


class Credito(Base):

    __tablename__ = "creditos"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False
    )

    tipo_credito = Column(
        String(100),
        default="Préstamo Personal"
    )

    monto_total = Column(
        Numeric(12, 2),
        default=0
    )

    cuota_mensual = Column(
        Numeric(12, 2),
        default=0
    )

    cuotas_totales = Column(
        Integer,
        default=12
    )

    cuotas_pagadas = Column(
        Integer,
        default=0
    )

    estado = Column(
        Enum(
            "Al día",
            "Pendiente",
            "Aprobado",
            "Rechazado",
            "Desembolsado",
            "Vencido",
            name="estado_credito"
        ),
        default="Pendiente"
    )

    fecha_creacion = Column(
        DateTime,
        server_default=func.now()
    )

    usuario = relationship(
        "Usuario",
        back_populates="creditos"
    )


class Transferencia(Base):

    __tablename__ = "transferencias"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False
    )

    cuenta_destino = Column(
        String(20),
        nullable=False
    )

    destinatario = Column(
        String(120),
        nullable=False
    )

    monto = Column(
        Numeric(12, 2),
        nullable=False
    )

    motivo = Column(String(150))

    fecha = Column(
        DateTime,
        server_default=func.now()
    )

    usuario = relationship(
        "Usuario",
        back_populates="transferencias"
    )


class Pago(Base):

    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False
    )

    servicio = Column(
        String(100),
        nullable=False
    )

    codigo_cliente = Column(
        String(50),
        nullable=False
    )

    monto = Column(
        Numeric(12, 2),
        nullable=False
    )

    fecha = Column(
        DateTime,
        server_default=func.now()
    )

    usuario = relationship(
        "Usuario",
        back_populates="pagos"
    )


class Movimiento(Base):

    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False
    )

    descripcion = Column(
        String(150),
        nullable=False
    )

    monto = Column(
        Numeric(12, 2),
        nullable=False
    )

    tipo = Column(
        Enum(
            "entrada",
            "salida",
            name="tipo_movimiento"
        ),
        nullable=False
    )

    fecha = Column(
        DateTime,
        server_default=func.now()
    )

    usuario = relationship(
        "Usuario",
        back_populates="movimientos"
    )