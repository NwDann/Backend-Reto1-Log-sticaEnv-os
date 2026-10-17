from sqlalchemy.orm import Session
from typing import List
from ..entities.ruta import Ruta, EstadoRuta
from ..entities.contrato import Contrato
from ..entities.despacho import Despacho
from ..models.ruta_mdl import (
    RutaCreate,
    RutaUpdate,
    RutaResponse,
    ActualizarEstadoRutaRequest,
)
from ..exceptions import RutaNotFoundError, EstadoRutaInvalidoError


class RutaService:
    @staticmethod
    def get_all(db: Session) -> List[RutaResponse]:
        rutas = db.query(Ruta).all()
        return [RutaResponse.model_validate(r) for r in rutas]

    @staticmethod
    def get_by_id(db: Session, ruta_id: int) -> RutaResponse:
        ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
        if not ruta:
            raise RutaNotFoundError(ruta_id)
        return RutaResponse.model_validate(ruta)

    @staticmethod
    def create(db: Session, data: RutaCreate) -> RutaResponse:
        payload = data.model_dump()
        # estado por defecto
        payload["estado"] = EstadoRuta.PLANIFICADA.value
        ruta = Ruta(**payload)
        db.add(ruta)
        db.commit()
        db.refresh(ruta)
        return RutaResponse.model_validate(ruta)

    @staticmethod
    def update(db: Session, ruta_id: int, data: RutaUpdate) -> RutaResponse:
        ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
        if not ruta:
            raise RutaNotFoundError(ruta_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            if field == "estado" and value is not None:
                try:
                    value = value.value if hasattr(value, "value") else value
                    # validar que sea un estado permitido
                    EstadoRuta(value)
                except ValueError:
                    raise EstadoRutaInvalidoError(str(value))
            setattr(ruta, field, value)
        db.commit()
        db.refresh(ruta)
        return RutaResponse.model_validate(ruta)

    @staticmethod
    def actualizar_estado(
        db: Session, ruta_id: int, data: ActualizarEstadoRutaRequest
    ) -> dict:
        """
        Actualiza el estado del viaje y registra cambios imprevistos o adendas
        si el servicio lo requiere sobre la marcha.
        """
        ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
        if not ruta:
            raise RutaNotFoundError(ruta_id)

        try:
            nuevo_estado_val = data.estado.value if hasattr(data.estado, "value") else data.estado
            EstadoRuta(nuevo_estado_val)  # valida
        except ValueError:
            raise EstadoRutaInvalidoError(str(data.estado))

        estado_anterior = ruta.estado if isinstance(ruta.estado, str) else str(ruta.estado)
        ruta.estado = nuevo_estado_val

        adendas_registradas = []
        if data.tiene_adenda or data.notas_imprevisto:
            # Buscar despachos de esta ruta y sus puntos → contratos
            despachos = db.query(Despacho).filter(Despacho.ruta_id == ruta_id).all()
            for d in despachos:
                contratos = (
                    db.query(Contrato)
                    .filter(
                        Contrato.punto_servicio_id == d.punto_servicio_id,
                        Contrato.vigente == True,  # noqa: E712
                    )
                    .all()
                )
                for c in contratos:
                    c.tiene_adenda = True
                    if data.notas_imprevisto:
                        extra = (
                            f"\n[Adenda ruta {ruta_id} - {estado_anterior}→{nuevo_estado_val}]: "
                            f"{data.notas_imprevisto}"
                        )
                        c.detalles_acuerdo = (c.detalles_acuerdo or "") + extra
                    adendas_registradas.append(c.id)

        db.commit()
        db.refresh(ruta)

        return {
            "ruta_id": ruta.id,
            "estado_anterior": estado_anterior,
            "estado_nuevo": nuevo_estado_val,
            "adendas_actualizadas": adendas_registradas,
            "notas": data.notas_imprevisto,
            "ruta": RutaResponse.model_validate(ruta),
        }

    @staticmethod
    def delete(db: Session, ruta_id: int) -> dict:
        ruta = db.query(Ruta).filter(Ruta.id == ruta_id).first()
        if not ruta:
            raise RutaNotFoundError(ruta_id)
        db.delete(ruta)
        db.commit()
        return {"message": f"Ruta {ruta_id} eliminada"}
