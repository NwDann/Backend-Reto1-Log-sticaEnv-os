from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class EstadoRutaEnum(str, Enum):
    PLANIFICADA = "Planificada"
    EN_TRANSITO = "En Tránsito"
    COMPLETADA = "Completada"


class RutaBase(BaseModel):
    codigo_vehiculo: str
    conductor_id: Optional[int] = None
    capacidad_peso_max_kg: float = 2000.0
    capacidad_volumen_max_m3: float = 0.0
    es_multiparada: bool = True


class RutaCreate(RutaBase):
    pass


class RutaUpdate(BaseModel):
    codigo_vehiculo: Optional[str] = None
    conductor_id: Optional[int] = None
    capacidad_peso_max_kg: Optional[float] = None
    capacidad_volumen_max_m3: Optional[float] = None
    peso_actual_carga: Optional[float] = None
    valor_mercaderia_total: Optional[float] = None
    es_multiparada: Optional[bool] = None
    estado: Optional[EstadoRutaEnum] = None


class ActualizarEstadoRutaRequest(BaseModel):
    estado: EstadoRutaEnum
    notas_imprevisto: Optional[str] = None  # para registrar adendas o cambios sobre la marcha
    tiene_adenda: bool = False


class RutaResponse(RutaBase):
    id: int
    peso_actual_carga: float
    valor_mercaderia_total: float
    estado: EstadoRutaEnum
    created_at: datetime

    class Config:
        from_attributes = True
