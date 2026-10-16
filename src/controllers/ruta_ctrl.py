from fastapi import APIRouter, status
from typing import List
from ..database.core import DbSession
from ..services.ruta_svc import RutaService
from ..models.ruta_mdl import (
    RutaCreate,
    RutaUpdate,
    RutaResponse,
    ActualizarEstadoRutaRequest,
)

router = APIRouter(prefix="/api/rutas", tags=["Rutas"])


@router.get("", response_model=List[RutaResponse])
def listar_rutas(db: DbSession):
    return RutaService.get_all(db)


@router.get("/{ruta_id}", response_model=RutaResponse)
def obtener_ruta(ruta_id: int, db: DbSession):
    return RutaService.get_by_id(db, ruta_id)


@router.post("", response_model=RutaResponse, status_code=status.HTTP_201_CREATED)
def crear_ruta(data: RutaCreate, db: DbSession):
    return RutaService.create(db, data)


@router.patch("/{ruta_id}", response_model=RutaResponse)
def actualizar_ruta(ruta_id: int, data: RutaUpdate, db: DbSession):
    return RutaService.update(db, ruta_id, data)


@router.patch("/{ruta_id}/estado")
def actualizar_estado_ruta(ruta_id: int, data: ActualizarEstadoRutaRequest, db: DbSession):
    """
    Actualiza el estado del viaje (Planificada, En Tránsito, Completada)
    y registra cambios de ruta imprevistos o adendas si el servicio lo requiere.
    """
    return RutaService.actualizar_estado(db, ruta_id, data)


@router.delete("/{ruta_id}")
def eliminar_ruta(ruta_id: int, db: DbSession):
    return RutaService.delete(db, ruta_id)
