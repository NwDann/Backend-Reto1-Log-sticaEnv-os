from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from ..database.core import Base


class Contrato(Base):
    __tablename__ = "contratos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    punto_servicio_id = Column(Integer, ForeignKey("puntos_servicio.id"), nullable=False)
    detalles_acuerdo = Column(String, nullable=True)
    tiene_adenda = Column(Boolean, default=False, nullable=False)
    vigente = Column(Boolean, default=True, nullable=False)

    # Relaciones
    punto_servicio = relationship("PuntoServicio", back_populates="contratos")
