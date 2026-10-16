from fastapi import APIRouter, status
from typing import List
from ..database.core import DbSession
from ..services.despacho_svc import DespachoService
from ..models.despacho_mdl import (
    DespachoCreate,
    DespachoUpdate,
    DespachoResponse,
)

router = APIRouter(prefix="/api/despachos", tags=["Despachos"])


@router.get("", response_model=List[DespachoResponse])
def listar_despachos(db: DbSession):
    return DespachoService.get_all(db)


@router.get("/{despacho_id}", response_model=DespachoResponse)
def obtener_despacho(despacho_id: int, db: DbSession):
    return DespachoService.get_by_id(db, despacho_id)


@router.post("", response_model=DespachoResponse, status_code=status.HTTP_201_CREATED)
def crear_despacho(data: DespachoCreate, db: DbSession):
    """
    Crea orden de despacho (programada semanal/quincenal o emergencia no programada).
    Soporta desglose por tipo de empaque e incluye banderas de promoción.
    """
    return DespachoService.create(db, data)


@router.patch("/{despacho_id}/apurar-produccion", response_model=DespachoResponse)
def apurar_produccion(despacho_id: int, db: DbSession):
    """
    Cambia el estado de producción a 'Apurado/Urgente' para reaccionar ante
    imprevistos, priorizando fabricación y re-enrutamiento inmediato.
    """
    return DespachoService.apurar_produccion(db, despacho_id)


@router.patch("/{despacho_id}", response_model=DespachoResponse)
def actualizar_despacho(despacho_id: int, data: DespachoUpdate, db: DbSession):
    return DespachoService.update(db, despacho_id, data)


@router.delete("/{despacho_id}")
def eliminar_despacho(despacho_id: int, db: DbSession):
    return DespachoService.delete(db, despacho_id)
