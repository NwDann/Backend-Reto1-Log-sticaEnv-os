from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class EstadoProduccionEnum(str, Enum):
    NORMAL = "Normal"
    APURADO_URGENTE = "Apurado/Urgente"


class DetalleDespachoCreate(BaseModel):
    insumo_id: int
    cantidad_solicitada: float
    es_promocion: bool = False


class DetalleDespachoResponse(BaseModel):
    id: int
    insumo_id: int
    cantidad_solicitada: float
    es_promocion: bool

    class Config:
        from_attributes = True


class DespachoCreate(BaseModel):
    punto_servicio_id: int
    fecha_programada: Optional[datetime] = None
    ruta_id: Optional[int] = None
    costo_envio: Optional[float] = None
    detalles: List[DetalleDespachoCreate] = Field(default_factory=list)
    # Si True, descuenta stock al crear (por defecto sí para control de inventarios)
    descontar_stock: bool = True


class DespachoUpdate(BaseModel):
    ruta_id: Optional[int] = None
    estado_produccion: Optional[EstadoProduccionEnum] = None
    fecha_programada: Optional[datetime] = None
    fecha_entrega_real: Optional[datetime] = None
    costo_envio: Optional[float] = None


class DespachoResponse(BaseModel):
    id: int
    ruta_id: Optional[int]
    punto_servicio_id: int
    estado_produccion: str
    fecha_programada: Optional[datetime]
    fecha_entrega_real: Optional[datetime]
    costo_envio: Optional[float]
    detalles: List[DetalleDespachoResponse] = []

    class Config:
        from_attributes = True
