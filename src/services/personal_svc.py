from sqlalchemy.orm import Session
from typing import List, Optional
from ..entities.personal import Personal, EspecialidadPersonal
from ..models.personal_mdl import (
    PersonalCreate,
    PersonalUpdate,
    PersonalResponse,
    ValidarAcreditacionResponse,
)
from ..exceptions import PersonalNotFoundError


class PersonalService:
    @staticmethod
    def get_all(db: Session) -> List[PersonalResponse]:
        personal = db.query(Personal).all()
        return [PersonalResponse.model_validate(p) for p in personal]

    @staticmethod
    def get_by_id(db: Session, personal_id: int) -> PersonalResponse:
        p = db.query(Personal).filter(Personal.id == personal_id).first()
        if not p:
            raise PersonalNotFoundError(personal_id)
        return PersonalResponse.model_validate(p)

    @staticmethod
    def create(db: Session, data: PersonalCreate) -> PersonalResponse:
        p = Personal(**data.model_dump())
        db.add(p)
        db.commit()
        db.refresh(p)
        return PersonalResponse.model_validate(p)

    @staticmethod
    def update(db: Session, personal_id: int, data: PersonalUpdate) -> PersonalResponse:
        p = db.query(Personal).filter(Personal.id == personal_id).first()
        if not p:
            raise PersonalNotFoundError(personal_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(p, field, value)
        db.commit()
        db.refresh(p)
        return PersonalResponse.model_validate(p)

    @staticmethod
    def delete(db: Session, personal_id: int) -> dict:
        p = db.query(Personal).filter(Personal.id == personal_id).first()
        if not p:
            raise PersonalNotFoundError(personal_id)
        db.delete(p)
        db.commit()
        return {"message": f"Personal {personal_id} eliminado"}

    @staticmethod
    def validar_acreditacion(
        db: Session,
        especialidad: Optional[str] = None,
        solo_disponibles: bool = True,
        requiere_acreditado: bool = True,
    ) -> ValidarAcreditacionResponse:
        """
        Filtra y retorna personal/cuadrillas con acreditación vigente
        requerida para puntos sensibles (hospitales) o emergencias.
        """
        query = db.query(Personal)
        if requiere_acreditado:
            query = query.filter(Personal.acreditado == True)
        if solo_disponibles:
            query = query.filter(Personal.disponible == True)
        if especialidad:
            try:
                esp = EspecialidadPersonal(especialidad)
                query = query.filter(Personal.especialidad == esp)
            except ValueError:
                pass  # especialidad inválida se ignora, se devuelve todo acreditado

        personal = query.all()
        return ValidarAcreditacionResponse(
            personal_disponible_acreditado=[PersonalResponse.model_validate(p) for p in personal],
            total=len(personal),
            filtro_especialidad=especialidad,
            filtro_requiere_acreditado=requiere_acreditado,
        )
