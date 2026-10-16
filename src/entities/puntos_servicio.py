from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
)
from datetime import datetime
from sqlalchemy.orm import relationship
from ..database.core import Base


class PuntoServicio(Base):
    __tablename__ = "puntos_servicio"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_cliente = Column(String, nullable=False)
    direccion = Column(String, nullable=True)
    zona_reparto = Column(String, nullable=True)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    metros_cuadrados_atendidos = Column(Float, nullable=True)
    requiere_personal_acreditado = Column(Boolean, default=False, nullable=False)
    contrato_validado = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    despachos = relationship("Despacho", back_populates="punto_servicio")
    contratos = relationship("Contrato", back_populates="punto_servicio")
