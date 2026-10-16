from sqlalchemy import (
    Column,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Enum as PgEnum,
)
from datetime import datetime
from sqlalchemy.orm import relationship
from enum import Enum
from ..database.core import Base


class TipoOrden(str, Enum):
    PROGRAMADA_QUINCENAL = "programada_quincenal"
    PROGRAMADA_SEMANAL = "programada_semanal"
    EMERGENCIA_NO_PROGRAMADA = "emergencia_no_programada"


class EstadoProduccion(str, Enum):
    NORMAL = "Normal"
    APURADO_URGENTE = "Apurado/Urgente"


class Despacho(Base):
    __tablename__ = "despachos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ruta_id = Column(Integer, ForeignKey("rutas.id"), nullable=True)
    punto_servicio_id = Column(Integer, ForeignKey("puntos_servicio.id"), nullable=False)
    tipo_orden = Column(PgEnum(TipoOrden), default=TipoOrden.PROGRAMADA_SEMANAL, nullable=False)
    estado_produccion = Column(PgEnum(EstadoProduccion), default=EstadoProduccion.NORMAL, nullable=False)
    fecha_programada = Column(DateTime, nullable=True)
    fecha_entrega_real = Column(DateTime, nullable=True)
    costo_envio = Column(Float, nullable=True)

    # Relaciones
    ruta = relationship("Ruta", back_populates="despachos")
    punto_servicio = relationship("PuntoServicio", back_populates="despachos")
    detalles = relationship("DetalleDespacho", back_populates="despacho", cascade="all, delete-orphan")
