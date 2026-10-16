from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Enum as PgEnum,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from ..database.core import Base


class CategoriaInsumo(str, Enum):
    QUIMICO = "quimico"
    CONSUMIBLE = "consumible"
    HERRAMIENTA = "herramienta"


class UnidadMedida(str, Enum):
    UNIDAD = "unidad"
    CAJA = "caja"
    CANECA = "caneca"
    LITRO = "litro"


class Insumo(Base):
    __tablename__ = "insumos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    categoria = Column(PgEnum(CategoriaInsumo), nullable=False)
    unidad_medida = Column(PgEnum(UnidadMedida), default=UnidadMedida.UNIDAD, nullable=False)
    peso_unitario_kg = Column(Float, default=0.0, nullable=False)
    volumen_unitario_m3 = Column(Float, default=0.0, nullable=False)
    stock_actual = Column(Float, default=0.0, nullable=False)
    stock_minimo = Column(Float, default=0.0, nullable=False)
    precio_unitario = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    detalles_despacho = relationship("DetalleDespacho", back_populates="insumo")
