from fastapi import APIRouter, status, Query
from typing import List, Optional
from ..database.core import DbSession
from ..services.personal_svc import PersonalService
from ..models.personal_mdl import (
    PersonalCreate,
    PersonalUpdate,
    PersonalResponse,
    ValidarAcreditacionResponse,
)

router = APIRouter(prefix="/api/personal", tags=["Personal"])


@router.get("", response_model=List[PersonalResponse])
def listar_personal(db: DbSession):
    return PersonalService.get_all(db)


@router.get("/validar-acreditacion", response_model=ValidarAcreditacionResponse)
def validar_acreditacion(
    db: DbSession,
    especialidad: Optional[str] = Query(None, description="general | hospitalario | emergencia"),
    solo_disponibles: bool = Query(True),
    requiere_acreditado: bool = Query(True),
):
    """
    Filtra y asigna cuadrillas/personal especializado con acreditación vigente
    requerida para puntos sensibles (clínicas/hospitales) o emergencias.
    """
    return PersonalService.validar_acreditacion(
        db, especialidad=especialidad, solo_disponibles=solo_disponibles, requiere_acreditado=requiere_acreditado
    )


@router.get("/{personal_id}", response_model=PersonalResponse)
def obtener_personal(personal_id: int, db: DbSession):
    return PersonalService.get_by_id(db, personal_id)


@router.post("", response_model=PersonalResponse, status_code=status.HTTP_201_CREATED)
def crear_personal(data: PersonalCreate, db: DbSession):
    return PersonalService.create(db, data)


@router.patch("/{personal_id}", response_model=PersonalResponse)
def actualizar_personal(personal_id: int, data: PersonalUpdate, db: DbSession):
    return PersonalService.update(db, personal_id, data)


@router.delete("/{personal_id}")
def eliminar_personal(personal_id: int, db: DbSession):
    return PersonalService.delete(db, personal_id)
