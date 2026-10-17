from sqlalchemy import (
    Column,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    String,
)
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from enum import Enum
from ..database.core import Base


class EstadoProduccion(str, Enum):
    NORMAL = "Normal"
    APURADO_URGENTE = "Apurado/Urgente"


class Despacho(Base):
    __tablename__ = "despachos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ruta_id = Column(Integer, ForeignKey("rutas.id", ondelete="SET NULL"), nullable=True)
    punto_servicio_id = Column(Integer, ForeignKey("puntos_servicio.id", ondelete="CASCADE"), nullable=False)
    # Alineado al esquema real: solo estado_produccion (VARCHAR + CHECK)
    estado_produccion = Column(String(50), default=EstadoProduccion.NORMAL.value, nullable=False)
    fecha_programada = Column(DateTime(timezone=True), nullable=True)
    fecha_entrega_real = Column(DateTime(timezone=True), nullable=True)
    costo_envio = Column(Float, nullable=True)

    # Relaciones
    ruta = relationship("Ruta", back_populates="despachos")
    punto_servicio = relationship("PuntoServicio", back_populates="despachos")
    detalles = relationship("DetalleDespacho", back_populates="despacho", cascade="all, delete-orphan")
