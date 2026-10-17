from sqlalchemy.orm import Session
from typing import List
from ..entities.insumo import Insumo, CategoriaInsumo
from ..entities.detalle_despacho import DetalleDespacho
from ..entities.puntos_servicio import PuntoServicio
from ..models.insumo_mdl import (
    InsumoCreate,
    InsumoUpdate,
    InsumoResponse,
    InsumoCriticoResponse,
    CalcularSugeridoRequest,
    CalcularSugeridoResponse,
)
from ..exceptions import InsumoNotFoundError, PuntoServicioNotFoundError, ValidationError


# Consumo por m² por defecto según categoría (litros o unidades)
CONSUMO_DEFAULT_POR_M2 = {
    CategoriaInsumo.QUIMICO.value: 0.05,      # 0.05 L por m²
    CategoriaInsumo.CONSUMIBLE.value: 0.02,
    CategoriaInsumo.HERRAMIENTA.value: 0.001,
}


class InsumoService:
    @staticmethod
    def get_all(db: Session) -> List[InsumoResponse]:
        insumos = db.query(Insumo).all()
        return [InsumoResponse.model_validate(i) for i in insumos]

    @staticmethod
    def get_by_id(db: Session, insumo_id: int) -> InsumoResponse:
        insumo = db.query(Insumo).filter(Insumo.id == insumo_id).first()
        if not insumo:
            raise InsumoNotFoundError(insumo_id)
        return InsumoResponse.model_validate(insumo)

    @staticmethod
    def create(db: Session, data: InsumoCreate) -> InsumoResponse:
        payload = data.model_dump()
        # Asegurar que los enums se guarden como string
        if hasattr(payload.get("categoria"), "value"):
            payload["categoria"] = payload["categoria"].value
        if hasattr(payload.get("unidad_medida"), "value"):
            payload["unidad_medida"] = payload["unidad_medida"].value
        insumo = Insumo(**payload)
        db.add(insumo)
        db.commit()
        db.refresh(insumo)
        return InsumoResponse.model_validate(insumo)

    @staticmethod
    def update(db: Session, insumo_id: int, data: InsumoUpdate) -> InsumoResponse:
        insumo = db.query(Insumo).filter(Insumo.id == insumo_id).first()
        if not insumo:
            raise InsumoNotFoundError(insumo_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            if hasattr(value, "value"):
                value = value.value
            setattr(insumo, field, value)
        db.commit()
        db.refresh(insumo)
        return InsumoResponse.model_validate(insumo)

    @staticmethod
    def delete(db: Session, insumo_id: int) -> dict:
        insumo = db.query(Insumo).filter(Insumo.id == insumo_id).first()
        if not insumo:
            raise InsumoNotFoundError(insumo_id)
        db.delete(insumo)
        db.commit()
        return {"message": f"Insumo {insumo_id} eliminado"}

    @staticmethod
    def get_criticos_y_proyeccion(db: Session) -> List[InsumoCriticoResponse]:
        """
        Analiza stock actual vs mínimo y cruza con despachos históricos
        para proyectar puntos de servicio en riesgo de quedarse sin suministro.
        """
        criticos = (
            db.query(Insumo)
            .filter(Insumo.stock_actual <= Insumo.stock_minimo)
            .all()
        )
        resultado = []
        for insumo in criticos:
            deficit = max(0.0, (insumo.stock_minimo or 0) - (insumo.stock_actual or 0))
            # Puntos que tienen despachos de este insumo
            detalles = (
                db.query(DetalleDespacho)
                .filter(DetalleDespacho.insumo_id == insumo.id)
                .all()
            )
            puntos_ids = set()
            puntos_info = []
            for det in detalles:
                despacho = det.despacho
                if not despacho:
                    continue
                if despacho.punto_servicio_id in puntos_ids:
                    continue
                puntos_ids.add(despacho.punto_servicio_id)
                punto = despacho.punto_servicio
                # Estimación simple de días de riesgo según si hay fecha programada
                if despacho.fecha_programada:
                    dias_riesgo = 7
                else:
                    dias_riesgo = 3  # emergencia / sin programar → riesgo más cercano
                puntos_info.append({
                    "punto_servicio_id": punto.id if punto else despacho.punto_servicio_id,
                    "nombre_cliente": punto.nombre_cliente if punto else "N/A",
                    "estado_produccion": despacho.estado_produccion,
                    "dias_estimados_sin_suministro": dias_riesgo,
                    "cantidad_ultima_solicitada": det.cantidad_solicitada,
                })
            resultado.append(
                InsumoCriticoResponse(
                    insumo=InsumoResponse.model_validate(insumo),
                    stock_deficit=deficit,
                    puntos_en_riesgo=puntos_info,
                )
            )
        return resultado

    @staticmethod
    def calcular_sugerido(db: Session, req: CalcularSugeridoRequest) -> CalcularSugeridoResponse:
        """
        Toma metros_cuadrados_atendidos del cliente y aplica fórmula de consumo
        (ej. litros por m²) para devolver cantidad exacta a despachar.
        """
        punto = db.query(PuntoServicio).filter(PuntoServicio.id == req.punto_servicio_id).first()
        if not punto:
            raise PuntoServicioNotFoundError(req.punto_servicio_id)

        insumo = db.query(Insumo).filter(Insumo.id == req.insumo_id).first()
        if not insumo:
            raise InsumoNotFoundError(req.insumo_id)

        metros = punto.metros_cuadrados_atendidos or 0.0
        if metros <= 0:
            raise ValidationError("El punto de servicio no tiene metros_cuadrados_atendidos definidos")

        consumo = req.consumo_por_m2
        if consumo is None:
            cat = insumo.categoria
            if hasattr(cat, "value"):
                cat = cat.value
            consumo = CONSUMO_DEFAULT_POR_M2.get(str(cat), 0.02)

        cantidad = round(metros * consumo, 2)

        # Desglose según unidad de medida
        desglose = {}
        unidad = insumo.unidad_medida
        if hasattr(unidad, "value"):
            unidad = unidad.value
        unidad = str(unidad)

        if unidad == "caja":
            desglose = {"cajas": int(cantidad), "unidades_restantes": round(cantidad % 1, 2)}
        elif unidad == "caneca":
            desglose = {"canecas": int(cantidad), "litros_restantes": round(cantidad % 1, 2)}
        elif unidad == "litro":
            desglose = {"litros": cantidad, "canecas_equivalentes": round(cantidad / 20, 2)}
        else:
            desglose = {"unidades": cantidad}

        return CalcularSugeridoResponse(
            punto_servicio_id=punto.id,
            nombre_cliente=punto.nombre_cliente,
            metros_cuadrados=metros,
            insumo_id=insumo.id,
            nombre_insumo=insumo.nombre,
            unidad_medida=unidad,
            consumo_por_m2=consumo,
            cantidad_sugerida=cantidad,
            desglose_empaque=desglose,
        )
