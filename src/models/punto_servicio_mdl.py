from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PuntoServicioBase(BaseModel):
    nombre_cliente: str
    direccion: Optional[str] = None
    zona_reparto: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    metros_cuadrados_atendidos: Optional[float] = None
    requiere_personal_acreditado: bool = False
    contrato_validado: bool = True


class PuntoServicioCreate(PuntoServicioBase):
    pass


class PuntoServicioUpdate(BaseModel):
    nombre_cliente: Optional[str] = None
    direccion: Optional[str] = None
    zona_reparto: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    metros_cuadrados_atendidos: Optional[float] = None
    requiere_personal_acreditado: Optional[bool] = None
    contrato_validado: Optional[bool] = None


class PuntoServicioResponse(PuntoServicioBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
