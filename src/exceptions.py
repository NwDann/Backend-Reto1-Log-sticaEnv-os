from fastapi import HTTPException


class BaseAppError(HTTPException):
    """Clase base para todas las excepciones personalizadas"""
    pass


# ---------- Insumos ----------
class InsumoError(BaseAppError):
    pass


class InsumoNotFoundError(InsumoError):
    def __init__(self, insumo_id: int | None = None):
        message = "Insumo no encontrado" if insumo_id is None else f"Insumo con id {insumo_id} no encontrado"
        super().__init__(status_code=404, detail=message)


class InsumoCreationError(InsumoError):
    def __init__(self, error: str):
        super().__init__(status_code=500, detail=f"Error al crear insumo: {error}")


class StockInsuficienteError(InsumoError):
    def __init__(self, insumo_id: int, stock_actual: float, solicitado: float):
        super().__init__(
            status_code=400,
            detail=f"Stock insuficiente para insumo {insumo_id}. Disponible: {stock_actual}, solicitado: {solicitado}",
        )


# ---------- Puntos de Servicio ----------
class PuntoServicioError(BaseAppError):
    pass


class PuntoServicioNotFoundError(PuntoServicioError):
    def __init__(self, punto_id: int | None = None):
        message = "Punto de servicio no encontrado" if punto_id is None else f"Punto de servicio con id {punto_id} no encontrado"
        super().__init__(status_code=404, detail=message)


# ---------- Personal ----------
class PersonalError(BaseAppError):
    pass


class PersonalNotFoundError(PersonalError):
    def __init__(self, personal_id: int | None = None):
        message = "Personal no encontrado" if personal_id is None else f"Personal con id {personal_id} no encontrado"
        super().__init__(status_code=404, detail=message)


class PersonalNoAcreditadoError(PersonalError):
    def __init__(self, personal_id: int | None = None):
        message = "El personal no cuenta con acreditación vigente" if personal_id is None else f"Personal {personal_id} no está acreditado"
        super().__init__(status_code=403, detail=message)


# ---------- Rutas ----------
class RutaError(BaseAppError):
    pass


class RutaNotFoundError(RutaError):
    def __init__(self, ruta_id: int | None = None):
        message = "Ruta no encontrada" if ruta_id is None else f"Ruta con id {ruta_id} no encontrada"
        super().__init__(status_code=404, detail=message)


class EstadoRutaInvalidoError(RutaError):
    def __init__(self, estado: str):
        super().__init__(
            status_code=400,
            detail=f"Estado de ruta inválido: '{estado}'. Valores permitidos: Planificada, En Tránsito, Completada",
        )


class CapacidadExcedidaError(RutaError):
    def __init__(self, tipo: str, actual: float, maximo: float):
        super().__init__(
            status_code=400,
            detail=f"Capacidad de {tipo} excedida. Actual: {actual}, máximo: {maximo}",
        )


# ---------- Despachos ----------
class DespachoError(BaseAppError):
    pass


class DespachoNotFoundError(DespachoError):
    def __init__(self, despacho_id: int | None = None):
        message = "Despacho no encontrado" if despacho_id is None else f"Despacho con id {despacho_id} no encontrado"
        super().__init__(status_code=404, detail=message)


class DespachoCreationError(DespachoError):
    def __init__(self, error: str):
        super().__init__(status_code=500, detail=f"Error al crear despacho: {error}")


# ---------- Contratos ----------
class ContratoError(BaseAppError):
    pass


class ContratoNotFoundError(ContratoError):
    def __init__(self, contrato_id: int | None = None):
        message = "Contrato no encontrado" if contrato_id is None else f"Contrato con id {contrato_id} no encontrado"
        super().__init__(status_code=404, detail=message)


# ---------- Validación genérica ----------
class ValidationError(BaseAppError):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)
