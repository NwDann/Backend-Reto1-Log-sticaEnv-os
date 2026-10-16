from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import os

from dotenv import load_dotenv

# Cargar .env solo en desarrollo local (en Render no existe o no se usa)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Prioridad: variables de entorno del sistema (Render) > .env local
SQLALCHEMY_DATABASE_URL = (
    os.environ.get("DATABASE_URL")
    or os.environ.get("SQLALCHEMY_DATABASE_URL")
)

if not SQLALCHEMY_DATABASE_URL:
    # Fallback solo para desarrollo local con SQLite
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'src', 'database', 'logistica.db')}"

# Supabase / Render a veces entregan postgres:// ; SQLAlchemy 2 exige postgresql://
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# connect_args solo aplica a SQLite
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"prepare_threshold": None},
    pool_pre_ping=True,  # útil con Supabase / conexiones remotas
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]
