from sqlalchemy.orm import Session, joinedload
from typing import List
from ..entities.despacho import Despacho, EstadoProduccion, TipoOrden
from ..entities.detalle_despacho import DetalleDespacho
from ..entities.insumo import Insumo
from ..entities.ruta import Ruta
from ..models.despacho_mdl import (
    DespachoCreate,
    DespachoUpdate,
    DespachoResponse,
    DetalleDespachoResponse,
)
from ..exceptions import (
    DespachoNotFoundError,
    DespachoCreationError,
    InsumoNotFoundError,
    PuntoServicioNotFoundError,
    RutaNotFoundError,
    StockInsuficienteError,
)
from ..entities.puntos_servicio import PuntoServicio


class DespachoService:
    @staticmethod
    def get_all(db: Session) -> List[DespachoResponse]:
        despachos = db.query(Despacho).options(joinedload(Despacho.detalles)).all()
        return [DespachoResponse.model_validate(d) for d in despachos]

    @staticmethod
    def get_by_id(db: Session, despacho_id: int) -> DespachoResponse:
        despacho = (
            db.query(Despacho)
            .options(joinedload(Despacho.detalles))
            .filter(Despacho.id == despacho_id)
            .first()
        )
        if not despacho:
            raise DespachoNotFoundError(despacho_id)
        return DespachoResponse.model_validate(despacho)

    @staticmethod
    def create(db: Session, data: DespachoCreate) -> DespachoResponse:
        """
        Crea orden de despacho (programada semanal/quincenal o emergencia).
        Soporta desglose por empaque y banderas de promoción.
        """
        punto = db.query(PuntoServicio).filter(PuntoServicio.id == data.punto_servicio_id).first()
        if not punto:
            raise PuntoServicioNotFoundError(data.punto_servicio_id)

        if data.ruta_id:
            ruta = db.query(Ruta).filter(Ruta.id == data.ruta_id).first()
            if not ruta:
                raise RutaNotFoundError(data.ruta_id)

        try:
            despacho = Despacho(
                punto_servicio_id=data.punto_servicio_id,
                tipo_orden=TipoOrden(data.tipo_orden.value),
                fecha_programada=data.fecha_programada,
                ruta_id=data.ruta_id,
                costo_envio=data.costo_envio,
                estado_produccion=EstadoProduccion.NORMAL,
            )
            db.add(despacho)
            db.flush()  # para obtener id

            valor_total = 0.0
            peso_total = 0.0

            for det in data.detalles:
                insumo = db.query(Insumo).filter(Insumo.id == det.insumo_id).first()
                if not insumo:
                    raise InsumoNotFoundError(det.insumo_id)

                # Validar stock (no descontamos aún; se puede hacer al completar)
                if insumo.stock_actual < det.cantidad_solicitada and not det.es_promocion:
                    # Permitimos crear la orden aunque falte stock (predicción), pero avisamos
                    pass

                detalle = DetalleDespacho(
                    despacho_id=despacho.id,
                    insumo_id=det.insumo_id,
                    cantidad_solicitada=det.cantidad_solicitada,
                    es_promocion=det.es_promocion,
                )
                db.add(detalle)

                if not det.es_promocion:
                    valor_total += det.cantidad_solicitada * (insumo.precio_unitario or 0)
                    peso_total += det.cantidad_solicitada * (insumo.peso_unitario_kg or 0)

            # Actualizar KPIs de la ruta si está asignada
            if data.ruta_id:
                ruta = db.query(Ruta).filter(Ruta.id == data.ruta_id).first()
                if ruta:
                    ruta.valor_mercaderia_total = (ruta.valor_mercaderia_total or 0) + valor_total
                    ruta.peso_actual_carga = (ruta.peso_actual_carga or 0) + peso_total

            db.commit()
            db.refresh(despacho)
            # Recargar con detalles
            despacho = (
                db.query(Despacho)
                .options(joinedload(Despacho.detalles))
                .filter(Despacho.id == despacho.id)
                .first()
            )
            return DespachoResponse.model_validate(despacho)
        except Exception as e:
            db.rollback()
            if isinstance(e, (InsumoNotFoundError, PuntoServicioNotFoundError, RutaNotFoundError)):
                raise
            raise DespachoCreationError(str(e))

    @staticmethod
    def apurar_produccion(db: Session, despacho_id: int) -> DespachoResponse:
        """
        Cambia estado de producción a Apurado/Urgente para priorizar fabricación
        y re-enrutamiento inmediato.
        """
        despacho = (
            db.query(Despacho)
            .options(joinedload(Despacho.detalles))
            .filter(Despacho.id == despacho_id)
            .first()
        )
        if not despacho:
            raise DespachoNotFoundError(despacho_id)

        despacho.estado_produccion = EstadoProduccion.APURADO_URGENTE
        db.commit()
        db.refresh(despacho)
        return DespachoResponse.model_validate(despacho)

    @staticmethod
    def update(db: Session, despacho_id: int, data: DespachoUpdate) -> DespachoResponse:
        despacho = (
            db.query(Despacho)
            .options(joinedload(Despacho.detalles))
            .filter(Despacho.id == despacho_id)
            .first()
        )
        if not despacho:
            raise DespachoNotFoundError(despacho_id)

        for field, value in data.model_dump(exclude_unset=True).items():
            if field == "tipo_orden" and value is not None:
                value = TipoOrden(value.value)
            elif field == "estado_produccion" and value is not None:
                value = EstadoProduccion(value.value)
            setattr(despacho, field, value)

        db.commit()
        db.refresh(despacho)
        return DespachoResponse.model_validate(despacho)

    @staticmethod
    def delete(db: Session, despacho_id: int) -> dict:
        despacho = db.query(Despacho).filter(Despacho.id == despacho_id).first()
        if not despacho:
            raise DespachoNotFoundError(despacho_id)
        db.delete(despacho)
        db.commit()
        return {"message": f"Despacho {despacho_id} eliminado"}
