from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database.core import engine, Base
from .logging import configure_logging, LogLevels

# Importar entidades para que Base las registre
from .entities import (  # noqa: F401
    Insumo,
    PuntoServicio,
    Personal,
    Ruta,
    Despacho,
    DetalleDespacho,
    Contrato,
)

from .controllers import (
    insumo_router,
    inventario_router,
    punto_servicio_router,
    personal_router,
    ruta_router,
    despacho_router,
    contrato_router,
    kpi_router,
)

configure_logging(LogLevels.info)

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Logística - Control de Inventarios & Rutas",
    description=(
        "Backend del reto Hackathon: Control de Inventarios, Predicción de Demanda, "
        "Optimización de Rutas y Trazabilidad Logística."
    ),
    version="1.0.0",
)

origins = [
    "http://localhost:5173",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(insumo_router)
app.include_router(inventario_router)
app.include_router(punto_servicio_router)
app.include_router(personal_router)
app.include_router(ruta_router)
app.include_router(despacho_router)
app.include_router(contrato_router)
app.include_router(kpi_router)


@app.get("/")
def root():
    return {
        "message": "API Logística operativa",
        "docs": "/docs",
        "endpoints_especiales": [
            "PATCH /api/rutas/{ruta_id}/estado",
            "GET  /api/insumos/criticos-y-proyeccion",
            "POST /api/inventario/calcular-sugerido",
            "POST /api/despachos",
            "PATCH /api/despachos/{despacho_id}/apurar-produccion",
            "GET  /api/personal/validar-acreditacion",
            "GET  /api/kpis/resumen",
        ],
    }


@app.get("/health")
def health():
    return {"status": "ok"}
