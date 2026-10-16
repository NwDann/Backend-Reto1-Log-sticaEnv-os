from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Enum as PgEnum,
)
from datetime import datetime
from sqlalchemy.orm import relationship
from enum import Enum
from ..database.core import Base


class EstadoRuta(str, Enum):
    PLANIFICADA = "Planificada"
    EN_TRANSITO = "En Tránsito"
    COMPLETADA = "Completada"


class Ruta(Base):
    __tablename__ = "rutas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_vehiculo = Column(String, nullable=False)
    conductor_id = Column(Integer, ForeignKey("personal.id"), nullable=True)
    capacidad_peso_max_kg = Column(Float, default=2000.0, nullable=False)
    capacidad_volumen_max_m3 = Column(Float, default=0.0, nullable=False)
    peso_actual_carga = Column(Float, default=0.0, nullable=False)
    valor_mercaderia_total = Column(Float, default=0.0, nullable=False)
    es_multiparada = Column(Boolean, default=True, nullable=False)
    estado = Column(PgEnum(EstadoRuta), default=EstadoRuta.PLANIFICADA, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    conductor = relationship("Personal", back_populates="rutas_asignadas")
    despachos = relationship("Despacho", back_populates="ruta")
