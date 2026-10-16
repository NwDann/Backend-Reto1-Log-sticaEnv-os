from fastapi import APIRouter, status
from typing import List
from ..database.core import DbSession
from ..services.contrato_svc import ContratoService
from ..models.contrato_mdl import ContratoCreate, ContratoUpdate, ContratoResponse

router = APIRouter(prefix="/api/contratos", tags=["Contratos"])


@router.get("", response_model=List[ContratoResponse])
def listar_contratos(db: DbSession):
    return ContratoService.get_all(db)


@router.get("/{contrato_id}", response_model=ContratoResponse)
def obtener_contrato(contrato_id: int, db: DbSession):
    return ContratoService.get_by_id(db, contrato_id)


@router.post("", response_model=ContratoResponse, status_code=status.HTTP_201_CREATED)
def crear_contrato(data: ContratoCreate, db: DbSession):
    return ContratoService.create(db, data)


@router.patch("/{contrato_id}", response_model=ContratoResponse)
def actualizar_contrato(contrato_id: int, data: ContratoUpdate, db: DbSession):
    return ContratoService.update(db, contrato_id, data)


@router.delete("/{contrato_id}")
def eliminar_contrato(contrato_id: int, db: DbSession):
    return ContratoService.delete(db, contrato_id)
