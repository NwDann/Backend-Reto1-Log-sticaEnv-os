# Backend Reto Hackathon - Logística

API FastAPI para Control de Inventarios, Predicción de Demanda, Optimización de Rutas y Trazabilidad.

## Arranque

```bash
cd Backend-Reto1
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Docs interactivas: http://localhost:8000/docs

## Endpoints especiales del reto

| Método | Ruta | Descripción |
|--------|------|-------------|
| PATCH | `/api/rutas/{ruta_id}/estado` | Actualiza estado del viaje + adendas |
| GET | `/api/insumos/criticos-y-proyeccion` | Stock crítico + proyección de puntos en riesgo |
| POST | `/api/inventario/calcular-sugerido` | Calcula cantidad según m² del cliente |
| POST | `/api/despachos` | Crea orden (programada o emergencia) con detalles |
| PATCH | `/api/despachos/{id}/apurar-produccion` | Marca producción como Apurado/Urgente |
| GET | `/api/personal/validar-acreditacion` | Filtra personal acreditado disponible |
| GET | `/api/kpis/resumen` | OTIF, rentabilidad, mermas, cumplimiento contratos |

## Estructura

```
src/
  controllers/   # Routers FastAPI
  services/      # Lógica de negocio
  models/        # Schemas Pydantic
  entities/      # Modelos SQLAlchemy
  database/      # Engine y sesión
  exceptions.py
  main.py
```
