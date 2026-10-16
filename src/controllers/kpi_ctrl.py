from fastapi import APIRouter
from ..database.core import DbSession
from ..services.kpi_svc import KPIService
from ..models.kpi_mdl import KPIResumenResponse

router = APIRouter(prefix="/api/kpis", tags=["KPIs"])


@router.get("/resumen", response_model=KPIResumenResponse)
def resumen_kpis(db: DbSession):
    """
    Calcula y devuelve en tiempo real:
    - OTIF (On-Time In-Full)
    - Rentabilidad por Ruta (>= $1000 USD)
    - Tasa de Mermas
    - Cumplimiento de Contratos
    """
    return KPIService.get_resumen(db)
