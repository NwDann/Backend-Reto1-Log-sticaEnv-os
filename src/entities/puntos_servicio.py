from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
)
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from ..database.core import Base


class PuntoServicio(Base):
    __tablename__ = "puntos_servicio"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_cliente = Column(String(255), nullable=False)
    direccion = Column(Text, nullable=True)
    zona_reparto = Column(String(100), nullable=True)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    metros_cuadrados_atendidos = Column(Float, nullable=True)
    requiere_personal_acreditado = Column(Boolean, default=False, nullable=False)
    contrato_validado = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relaciones
    despachos = relationship("Despacho", back_populates="punto_servicio")
    contratos = relationship("Contrato", back_populates="punto_servicio")
