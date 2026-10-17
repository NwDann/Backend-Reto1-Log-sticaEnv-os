from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
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
    nombre = Column(String(255), nullable=False)
    # Almacenamos como VARCHAR para alinear con el CHECK del esquema Supabase
    categoria = Column(String(50), nullable=False)
    unidad_medida = Column(String(50), default=UnidadMedida.UNIDAD.value, nullable=False)
    peso_unitario_kg = Column(Float, default=0.0, nullable=False)
    volumen_unitario_m3 = Column(Float, default=0.0, nullable=False)
    stock_actual = Column(Float, default=0.0, nullable=False)
    stock_minimo = Column(Float, default=0.0, nullable=False)
    precio_unitario = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relaciones
    detalles_despacho = relationship("DetalleDespacho", back_populates="insumo")
