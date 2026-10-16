from pydantic import BaseModel


class KPIResumenResponse(BaseModel):
    otif_porcentaje: float  # On-Time In-Full
    otif_detalle: dict
    rentabilidad_por_ruta: dict  # viajes que cumplieron >= $1000
    tasa_mermas: float
    mermas_detalle: dict
    cumplimiento_contratos_porcentaje: float
    cumplimiento_contratos_detalle: dict
    total_rutas: int
    total_despachos: int
    total_contratos: int
