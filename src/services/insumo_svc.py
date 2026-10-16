from sqlalchemy.orm import Session
from typing import List, Optional
from ..entities.insumo import Insumo, CategoriaInsumo, UnidadMedida
from ..entities.despacho import Despacho, TipoOrden
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
    CategoriaInsumo.QUIMICO: 0.05,      # 0.05 L por m²
    CategoriaInsumo.CONSUMIBLE: 0.02,
    CategoriaInsumo.HERRAMIENTA: 0.001,
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
        insumo = Insumo(**data.model_dump())
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
        Analiza stock actual vs mínimo y cruza con frecuencia de despachos
        (semanal / quincenal) para proyectar puntos de servicio en riesgo.
        """
        criticos = (
            db.query(Insumo)
            .filter(Insumo.stock_actual <= Insumo.stock_minimo)
            .all()
        )
        resultado = []
        for insumo in criticos:
            deficit = insumo.stock_minimo - insumo.stock_actual
            # Puntos que tienen despachos recientes o programados de este insumo
            detalles = (
                db.query(DetalleDespacho)
                .filter(DetalleDespacho.insumo_id == insumo.id)
                .all()
            )
            puntos_ids = set()
            puntos_info = []
            for det in detalles:
                despacho = det.despacho
                if despacho and despacho.punto_servicio_id not in puntos_ids:
                    puntos_ids.add(despacho.punto_servicio_id)
                    punto = despacho.punto_servicio
                    frecuencia = despacho.tipo_orden.value if despacho.tipo_orden else "desconocida"
                    # Proyección simple: si es semanal, riesgo en ~7 días; quincenal ~14
                    dias_riesgo = 7 if "semanal" in frecuencia else (14 if "quincenal" in frecuencia else 3)
                    puntos_info.append({
                        "punto_servicio_id": punto.id if punto else despacho.punto_servicio_id,
                        "nombre_cliente": punto.nombre_cliente if punto else "N/A",
                        "tipo_orden_frecuencia": frecuencia,
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
            consumo = CONSUMO_DEFAULT_POR_M2.get(insumo.categoria, 0.02)

        cantidad = round(metros * consumo, 2)

        # Desglose según unidad de medida
        desglose = {}
        unidad = insumo.unidad_medida.value if hasattr(insumo.unidad_medida, "value") else str(insumo.unidad_medida)
        if unidad == "caja":
            desglose = {"cajas": int(cantidad), "unidades_restantes": round(cantidad % 1, 2)}
        elif unidad == "caneca":
            desglose = {"canecas": int(cantidad), "litros_restantes": round(cantidad % 1, 2)}
        elif unidad == "litro":
            desglose = {"litros": cantidad, "canecas_equivalentes": round(cantidad / 20, 2)}  # caneca ~20L
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
