from sqlalchemy.orm import Session
from typing import List
from ..entities.contrato import Contrato
from ..models.contrato_mdl import ContratoCreate, ContratoUpdate, ContratoResponse
from ..exceptions import ContratoNotFoundError, PuntoServicioNotFoundError
from ..entities.puntos_servicio import PuntoServicio


class ContratoService:
    @staticmethod
    def get_all(db: Session) -> List[ContratoResponse]:
        contratos = db.query(Contrato).all()
        return [ContratoResponse.model_validate(c) for c in contratos]

    @staticmethod
    def get_by_id(db: Session, contrato_id: int) -> ContratoResponse:
        c = db.query(Contrato).filter(Contrato.id == contrato_id).first()
        if not c:
            raise ContratoNotFoundError(contrato_id)
        return ContratoResponse.model_validate(c)

    @staticmethod
    def create(db: Session, data: ContratoCreate) -> ContratoResponse:
        punto = db.query(PuntoServicio).filter(PuntoServicio.id == data.punto_servicio_id).first()
        if not punto:
            raise PuntoServicioNotFoundError(data.punto_servicio_id)
        c = Contrato(**data.model_dump())
        db.add(c)
        db.commit()
        db.refresh(c)
        return ContratoResponse.model_validate(c)

    @staticmethod
    def update(db: Session, contrato_id: int, data: ContratoUpdate) -> ContratoResponse:
        c = db.query(Contrato).filter(Contrato.id == contrato_id).first()
        if not c:
            raise ContratoNotFoundError(contrato_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(c, field, value)
        db.commit()
        db.refresh(c)
        return ContratoResponse.model_validate(c)

    @staticmethod
    def delete(db: Session, contrato_id: int) -> dict:
        c = db.query(Contrato).filter(Contrato.id == contrato_id).first()
        if not c:
            raise ContratoNotFoundError(contrato_id)
        db.delete(c)
        db.commit()
        return {"message": f"Contrato {contrato_id} eliminado"}
