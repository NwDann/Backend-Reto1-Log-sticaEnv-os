from sqlalchemy.orm import Session
from typing import List
from ..entities.puntos_servicio import PuntoServicio
from ..models.punto_servicio_mdl import (
    PuntoServicioCreate,
    PuntoServicioUpdate,
    PuntoServicioResponse,
)
from ..exceptions import PuntoServicioNotFoundError


class PuntoServicioService:
    @staticmethod
    def get_all(db: Session) -> List[PuntoServicioResponse]:
        puntos = db.query(PuntoServicio).all()
        return [PuntoServicioResponse.model_validate(p) for p in puntos]

    @staticmethod
    def get_by_id(db: Session, punto_id: int) -> PuntoServicioResponse:
        punto = db.query(PuntoServicio).filter(PuntoServicio.id == punto_id).first()
        if not punto:
            raise PuntoServicioNotFoundError(punto_id)
        return PuntoServicioResponse.model_validate(punto)

    @staticmethod
    def create(db: Session, data: PuntoServicioCreate) -> PuntoServicioResponse:
        punto = PuntoServicio(**data.model_dump())
        db.add(punto)
        db.commit()
        db.refresh(punto)
        return PuntoServicioResponse.model_validate(punto)

    @staticmethod
    def update(db: Session, punto_id: int, data: PuntoServicioUpdate) -> PuntoServicioResponse:
        punto = db.query(PuntoServicio).filter(PuntoServicio.id == punto_id).first()
        if not punto:
            raise PuntoServicioNotFoundError(punto_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(punto, field, value)
        db.commit()
        db.refresh(punto)
        return PuntoServicioResponse.model_validate(punto)

    @staticmethod
    def delete(db: Session, punto_id: int) -> dict:
        punto = db.query(PuntoServicio).filter(PuntoServicio.id == punto_id).first()
        if not punto:
            raise PuntoServicioNotFoundError(punto_id)
        db.delete(punto)
        db.commit()
        return {"message": f"Punto de servicio {punto_id} eliminado"}
