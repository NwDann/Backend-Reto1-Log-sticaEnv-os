from pydantic import BaseModel
from typing import Optional


class ContratoBase(BaseModel):
    punto_servicio_id: int
    detalles_acuerdo: Optional[str] = None
    tiene_adenda: bool = False
    vigente: bool = True


class ContratoCreate(ContratoBase):
    pass


class ContratoUpdate(BaseModel):
    detalles_acuerdo: Optional[str] = None
    tiene_adenda: Optional[bool] = None
    vigente: Optional[bool] = None


class ContratoResponse(ContratoBase):
    id: int

    class Config:
        from_attributes = True
