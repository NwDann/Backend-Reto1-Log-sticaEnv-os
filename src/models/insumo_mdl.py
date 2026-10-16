from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class CategoriaInsumoEnum(str, Enum):
    quimico = "quimico"
    consumible = "consumible"
    herramienta = "herramienta"


class UnidadMedidaEnum(str, Enum):
    unidad = "unidad"
    caja = "caja"
    caneca = "caneca"
    litro = "litro"


class InsumoBase(BaseModel):
    nombre: str
    categoria: CategoriaInsumoEnum
    unidad_medida: UnidadMedidaEnum = UnidadMedidaEnum.unidad
    peso_unitario_kg: float = 0.0
    volumen_unitario_m3: float = 0.0
    stock_actual: float = 0.0
    stock_minimo: float = 0.0
    precio_unitario: float = 0.0


class InsumoCreate(InsumoBase):
    pass


class InsumoUpdate(BaseModel):
    nombre: Optional[str] = None
    categoria: Optional[CategoriaInsumoEnum] = None
    unidad_medida: Optional[UnidadMedidaEnum] = None
    peso_unitario_kg: Optional[float] = None
    volumen_unitario_m3: Optional[float] = None
    stock_actual: Optional[float] = None
    stock_minimo: Optional[float] = None
    precio_unitario: Optional[float] = None


class InsumoResponse(InsumoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class InsumoCriticoResponse(BaseModel):
    """Insumo con stock por debajo del mínimo + proyección de puntos afectados"""
    insumo: InsumoResponse
    stock_deficit: float
    puntos_en_riesgo: list[dict]


class CalcularSugeridoRequest(BaseModel):
    punto_servicio_id: int
    insumo_id: int
    # Fórmula: litros (o unidades) por m². Si no se envía, se usa un default por categoría
    consumo_por_m2: Optional[float] = None


class CalcularSugeridoResponse(BaseModel):
    punto_servicio_id: int
    nombre_cliente: str
    metros_cuadrados: float
    insumo_id: int
    nombre_insumo: str
    unidad_medida: str
    consumo_por_m2: float
    cantidad_sugerida: float
    desglose_empaque: dict  # ej: {"cajas": 2, "unidades": 5}
