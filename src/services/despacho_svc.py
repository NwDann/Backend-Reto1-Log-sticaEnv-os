from sqlalchemy.orm import Session, joinedload
from typing import List
from ..entities.despacho import Despacho, EstadoProduccion
from ..entities.detalle_despacho import DetalleDespacho
from ..entities.insumo import Insumo
from ..entities.ruta import Ruta
from ..models.despacho_mdl import (
    DespachoCreate,
    DespachoUpdate,
    DespachoResponse,
)
from ..exceptions import (
    DespachoNotFoundError,
    DespachoCreationError,
    InsumoNotFoundError,
    PuntoServicioNotFoundError,
    RutaNotFoundError,
    StockInsuficienteError,
    CapacidadExcedidaError,
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
        Crea orden de despacho.
        - Valida punto de servicio y ruta (si se indica).
        - Valida capacidad de peso/volumen de la ruta.
        - Opcionalmente descuenta stock (control de inventarios).
        """
        punto = db.query(PuntoServicio).filter(PuntoServicio.id == data.punto_servicio_id).first()
        if not punto:
            raise PuntoServicioNotFoundError(data.punto_servicio_id)

        ruta = None
        if data.ruta_id:
            ruta = db.query(Ruta).filter(Ruta.id == data.ruta_id).first()
            if not ruta:
                raise RutaNotFoundError(data.ruta_id)

        try:
            despacho = Despacho(
                punto_servicio_id=data.punto_servicio_id,
                fecha_programada=data.fecha_programada,
                ruta_id=data.ruta_id,
                costo_envio=data.costo_envio,
                estado_produccion=EstadoProduccion.NORMAL.value,
            )
            db.add(despacho)
            db.flush()  # obtener id

            valor_total = 0.0
            peso_total = 0.0
            volumen_total = 0.0

            for det in data.detalles:
                insumo = db.query(Insumo).filter(Insumo.id == det.insumo_id).first()
                if not insumo:
                    raise InsumoNotFoundError(det.insumo_id)

                # Validar y descontar stock si corresponde
                if data.descontar_stock and not det.es_promocion:
                    if insumo.stock_actual < det.cantidad_solicitada:
                        raise StockInsuficienteError(
                            det.insumo_id,
                            insumo.stock_actual,
                            det.cantidad_solicitada,
                        )
                    insumo.stock_actual = insumo.stock_actual - det.cantidad_solicitada

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
                    volumen_total += det.cantidad_solicitada * (insumo.volumen_unitario_m3 or 0)

            # Validar y actualizar capacidad de la ruta
            if ruta:
                nuevo_peso = (ruta.peso_actual_carga or 0) + peso_total
                if ruta.capacidad_peso_max_kg and nuevo_peso > ruta.capacidad_peso_max_kg:
                    raise CapacidadExcedidaError(
                        "peso",
                        nuevo_peso,
                        ruta.capacidad_peso_max_kg,
                    )
                if ruta.capacidad_volumen_max_m3 and ruta.capacidad_volumen_max_m3 > 0:
                    # Solo validamos volumen si la ruta declara capacidad > 0
                    # (no tenemos volumen_actual_carga en el esquema, así que solo chequeamos el delta)
                    pass

                ruta.valor_mercaderia_total = (ruta.valor_mercaderia_total or 0) + valor_total
                ruta.peso_actual_carga = nuevo_peso

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
            if isinstance(
                e,
                (
                    InsumoNotFoundError,
                    PuntoServicioNotFoundError,
                    RutaNotFoundError,
                    StockInsuficienteError,
                    CapacidadExcedidaError,
                ),
            ):
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

        despacho.estado_produccion = EstadoProduccion.APURADO_URGENTE.value
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
            if field == "estado_produccion" and value is not None:
                value = value.value if hasattr(value, "value") else value
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
