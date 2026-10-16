from fastapi import APIRouter, status
from typing import List
from ..database.core import DbSession
from ..services.insumo_svc import InsumoService
from ..models.insumo_mdl import (
    InsumoCreate,
    InsumoUpdate,
    InsumoResponse,
    InsumoCriticoResponse,
    CalcularSugeridoRequest,
    CalcularSugeridoResponse,
)

router = APIRouter(prefix="/api/insumos", tags=["Insumos"])


@router.get("", response_model=List[InsumoResponse])
def listar_insumos(db: DbSession):
    return InsumoService.get_all(db)


@router.get("/criticos-y-proyeccion", response_model=List[InsumoCriticoResponse])
def insumos_criticos_y_proyeccion(db: DbSession):
    """
    Analiza stock actual vs mínimo y cruza con frecuencia de clientes
    (despachos semanales/quincenales). Retorna puntos de servicio en riesgo.
    """
    return InsumoService.get_criticos_y_proyeccion(db)


@router.get("/{insumo_id}", response_model=InsumoResponse)
def obtener_insumo(insumo_id: int, db: DbSession):
    return InsumoService.get_by_id(db, insumo_id)


@router.post("", response_model=InsumoResponse, status_code=status.HTTP_201_CREATED)
def crear_insumo(data: InsumoCreate, db: DbSession):
    return InsumoService.create(db, data)


@router.patch("/{insumo_id}", response_model=InsumoResponse)
def actualizar_insumo(insumo_id: int, data: InsumoUpdate, db: DbSession):
    return InsumoService.update(db, insumo_id, data)


@router.delete("/{insumo_id}")
def eliminar_insumo(insumo_id: int, db: DbSession):
    return InsumoService.delete(db, insumo_id)
