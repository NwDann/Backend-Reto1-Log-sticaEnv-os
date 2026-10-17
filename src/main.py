from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .database.core import engine, Base
from .logging import configure_logging, LogLevels

# Importar entidades para que Base las registre
from .entities.insumo import Insumo
from .entities.puntos_servicio import PuntoServicio
from .entities.personal import Personal
from .entities.ruta import Ruta
from .entities.despacho import Despacho
from .entities.contrato import Contrato

from .controllers.insumo_ctrl import router as insumo_router
from .controllers.inventario_ctrl import router as inventario_router
from .controllers.punto_servicio_ctrl import router as punto_servicio_router
from .controllers.personal_ctrl import router as personal_router
from .controllers.ruta_ctrl import router as ruta_router
from .controllers.despacho_ctrl import router as despacho_router
from .controllers.contrato_ctrl import router as contrato_router
from .controllers.kpi_ctrl import router as kpi_router

configure_logging(LogLevels.info)

# Crear tablas si no existen (en Supabase ya las tienes; es idempotente)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Logística - Control de Inventarios & Rutas",
    description=(
        "Backend del reto Hackathon: Control de Inventarios, Predicción de Demanda, "
        "Optimización de Rutas y Trazabilidad Logística."
    ),
    version="1.0.0",
)

# En producción permite el origen del frontend; en local los típicos de Vite
origins = [
    "http://localhost:5173",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
]
# Añade tu dominio de frontend si lo tienes (ej. Vercel)
extra = os.environ.get("CORS_ORIGINS", "")
if extra:
    origins.extend([o.strip() for o in extra.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            "POST /api/despachos  (crea orden + opcional descuento de stock + validación capacidad)",
            "PATCH /api/despachos/{despacho_id}/apurar-produccion",
            "GET  /api/personal/validar-acreditacion",
            "GET  /api/kpis/resumen",
        ],
    }


@app.get("/health")
def health():
    return {"status": "ok"}