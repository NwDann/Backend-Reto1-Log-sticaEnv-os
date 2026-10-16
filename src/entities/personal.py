from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Enum as PgEnum,
)
from sqlalchemy.orm import relationship
from enum import Enum
from ..database.core import Base


class EspecialidadPersonal(str, Enum):
    GENERAL = "general"
    HOSPITALARIO = "hospitalario"
    EMERGENCIA = "emergencia"


class Personal(Base):
    __tablename__ = "personal"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    especialidad = Column(PgEnum(EspecialidadPersonal), default=EspecialidadPersonal.GENERAL, nullable=False)
    acreditado = Column(Boolean, default=True, nullable=False)
    disponible = Column(Boolean, default=True, nullable=False)

    # Relaciones
    rutas_asignadas = relationship("Ruta", back_populates="conductor")
