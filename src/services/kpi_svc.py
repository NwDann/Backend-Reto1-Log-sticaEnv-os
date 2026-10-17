from sqlalchemy.orm import Session, joinedload
from ..entities.ruta import Ruta, EstadoRuta
from ..entities.despacho import Despacho
from ..entities.contrato import Contrato
from ..entities.insumo import Insumo
from ..models.kpi_mdl import KPIResumenResponse


class KPIService:
    @staticmethod
    def get_resumen(db: Session) -> KPIResumenResponse:
        """
        Calcula KPIs en tiempo real:
        - OTIF (On-Time In-Full)
        - Rentabilidad por Ruta (>= $1000 USD en mercancía)
        - Tasa de Mermas
        - Cumplimiento de Contratos
        """
        rutas = db.query(Ruta).all()
        despachos = db.query(Despacho).options(joinedload(Despacho.detalles)).all()
        contratos = db.query(Contrato).options(joinedload(Contrato.punto_servicio)).all()

        total_rutas = len(rutas)
        total_despachos = len(despachos)
        total_contratos = len(contratos)

        # --- OTIF: entregas a tiempo y completas ---
        # Consideramos "a tiempo" si fecha_entrega_real <= fecha_programada (o sin programada = emergencia OK)
        # "In-Full" si el despacho tiene detalles (simplificado: existe al menos un detalle)
        on_time_in_full = 0
        on_time = 0
        in_full = 0
        entregados = 0

        for d in despachos:
            if d.fecha_entrega_real is not None:
                entregados += 1
                a_tiempo = True
                if d.fecha_programada and d.fecha_entrega_real > d.fecha_programada:
                    a_tiempo = False
                if a_tiempo:
                    on_time += 1

                completo = len(d.detalles) > 0 if d.detalles is not None else False
                # Alternativa: verificar que no haya stock negativo, pero usamos existencia de detalles
                if completo:
                    in_full += 1
                if a_tiempo and completo:
                    on_time_in_full += 1

        otif_pct = (on_time_in_full / entregados * 100) if entregados > 0 else 0.0

        # --- Rentabilidad por Ruta: viajes con valor_mercaderia_total >= 1000 ---
        rutas_rentables = [r for r in rutas if (r.valor_mercaderia_total or 0) >= 1000.0]
        rutas_completadas = [r for r in rutas if r.estado == EstadoRuta.COMPLETADA.value or r.estado == "Completada"]
        pct_rentables = (len(rutas_rentables) / total_rutas * 100) if total_rutas > 0 else 0.0

        # --- Tasa de Mermas: simplificado ---
        # Mermas = diferencia entre stock mínimo esperado vs actual en insumos críticos,
        # o pérdida estimada (si no hay tabla de mermas, usamos % de insumos bajo mínimo)
        insumos = db.query(Insumo).all()
        total_insumos = len(insumos)
        bajo_minimo = sum(1 for i in insumos if i.stock_actual < i.stock_minimo)
        tasa_mermas = (bajo_minimo / total_insumos * 100) if total_insumos > 0 else 0.0

        # --- Cumplimiento de Contratos ---
        # Contrato cumplido si vigente=True y el punto tiene contrato_validado
        cumplidos = 0
        for c in contratos:
            if c.vigente:
                punto = c.punto_servicio
                if punto and punto.contrato_validado:
                    cumplidos += 1
        cumplimiento_pct = (cumplidos / total_contratos * 100) if total_contratos > 0 else 100.0

        return KPIResumenResponse(
            otif_porcentaje=round(otif_pct, 2),
            otif_detalle={
                "entregas_totales": entregados,
                "on_time": on_time,
                "in_full": in_full,
                "on_time_in_full": on_time_in_full,
            },
            rentabilidad_por_ruta={
                "rutas_con_valor_gte_1000": len(rutas_rentables),
                "total_rutas": total_rutas,
                "porcentaje_cumplimiento_regla": round(pct_rentables, 2),
                "rutas_completadas": len(rutas_completadas),
                "umbral_usd": 1000.0,
            },
            tasa_mermas=round(tasa_mermas, 2),
            mermas_detalle={
                "insumos_bajo_minimo": bajo_minimo,
                "total_insumos": total_insumos,
                "nota": "Proxy basado en insumos con stock_actual < stock_minimo",
            },
            cumplimiento_contratos_porcentaje=round(cumplimiento_pct, 2),
            cumplimiento_contratos_detalle={
                "contratos_cumplidos": cumplidos,
                "total_contratos": total_contratos,
                "contratos_vigentes": sum(1 for c in contratos if c.vigente),
            },
            total_rutas=total_rutas,
            total_despachos=total_despachos,
            total_contratos=total_contratos,
        )
