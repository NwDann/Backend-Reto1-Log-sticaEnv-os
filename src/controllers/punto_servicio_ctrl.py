from fastapi import APIRouter, status
from typing import List
from ..database.core import DbSession
from ..services.punto_servicio_svc import PuntoServicioService
from ..models.punto_servicio_mdl import (
    PuntoServicioCreate,
    PuntoServicioUpdate,
    PuntoServicioResponse,
)

router = APIRouter(prefix="/api/puntos-servicio", tags=["Puntos de Servicio"])


@router.get("", response_model=List[PuntoServicioResponse])
def listar_puntos(db: DbSession):
    return PuntoServicioService.get_all(db)


@router.get("/{punto_id}", response_model=PuntoServicioResponse)
def obtener_punto(punto_id: int, db: DbSession):
    return PuntoServicioService.get_by_id(db, punto_id)


@router.post("", response_model=PuntoServicioResponse, status_code=status.HTTP_201_CREATED)
def crear_punto(data: PuntoServicioCreate, db: DbSession):
    return PuntoServicioService.create(db, data)


@router.patch("/{punto_id}", response_model=PuntoServicioResponse)
def actualizar_punto(punto_id: int, data: PuntoServicioUpdate, db: DbSession):
    return PuntoServicioService.update(db, punto_id, data)


@router.delete("/{punto_id}")
def eliminar_punto(punto_id: int, db: DbSession):
    return PuntoServicioService.delete(db, punto_id)
