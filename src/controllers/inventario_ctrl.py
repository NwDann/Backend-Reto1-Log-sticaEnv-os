from fastapi import APIRouter
from ..database.core import DbSession
from ..services.insumo_svc import InsumoService
from ..models.insumo_mdl import CalcularSugeridoRequest, CalcularSugeridoResponse

router = APIRouter(prefix="/api/inventario", tags=["Inventario"])


@router.post("/calcular-sugerido", response_model=CalcularSugeridoResponse)
def calcular_cantidad_sugerida(data: CalcularSugeridoRequest, db: DbSession):
    """
    Toma el área del cliente (metros_cuadrados_atendidos) y aplica la fórmula
    de consumo (ej. litros de producto por m²). Devuelve cantidad exacta
    de cajas, canecas o unidades a despachar.
    """
    return InsumoService.calcular_sugerido(db, data)
