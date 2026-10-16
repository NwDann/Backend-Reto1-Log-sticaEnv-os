from pydantic import BaseModel
from typing import Optional
from enum import Enum


class EspecialidadEnum(str, Enum):
    general = "general"
    hospitalario = "hospitalario"
    emergencia = "emergencia"


class PersonalBase(BaseModel):
    nombre: str
    especialidad: EspecialidadEnum = EspecialidadEnum.general
    acreditado: bool = True
    disponible: bool = True


class PersonalCreate(PersonalBase):
    pass


class PersonalUpdate(BaseModel):
    nombre: Optional[str] = None
    especialidad: Optional[EspecialidadEnum] = None
    acreditado: Optional[bool] = None
    disponible: Optional[bool] = None


class PersonalResponse(PersonalBase):
    id: int

    class Config:
        from_attributes = True


class ValidarAcreditacionResponse(BaseModel):
    personal_disponible_acreditado: list[PersonalResponse]
    total: int
    filtro_especialidad: Optional[str] = None
    filtro_requiere_acreditado: bool = True
