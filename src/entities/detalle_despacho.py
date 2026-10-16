from sqlalchemy import (
    Column,
    Integer,
    Float,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from ..database.core import Base


class DetalleDespacho(Base):
    __tablename__ = "detalle_despachos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    despacho_id = Column(Integer, ForeignKey("despachos.id"), nullable=False)
    insumo_id = Column(Integer, ForeignKey("insumos.id"), nullable=False)
    cantidad_solicitada = Column(Float, nullable=False)
    es_promocion = Column(Boolean, default=False, nullable=False)

    # Relaciones
    despacho = relationship("Despacho", back_populates="detalles")
    insumo = relationship("Insumo", back_populates="detalles_despacho")
