from .insumo import Insumo, CategoriaInsumo, UnidadMedida
from .puntos_servicio import PuntoServicio
from .personal import Personal, EspecialidadPersonal
from .ruta import Ruta, EstadoRuta
from .despacho import Despacho, EstadoProduccion
from .detalle_despacho import DetalleDespacho
from .contrato import Contrato

__all__ = [
    "Insumo",
    "CategoriaInsumo",
    "UnidadMedida",
    "PuntoServicio",
    "Personal",
    "EspecialidadPersonal",
    "Ruta",
    "EstadoRuta",
    "Despacho",
    "EstadoProduccion",
    "DetalleDespacho",
    "Contrato",
]
