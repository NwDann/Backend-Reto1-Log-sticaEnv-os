from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import os

from dotenv import dotenv_values

# Buscar .env en la raíz del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
config = dotenv_values(os.path.join(BASE_DIR, ".env"))

SQLALCHEMY_DATABASE_URL = config.get(
    "SQLALCHEMY_DATABASE_URL",
    f"sqlite:///{os.path.join(BASE_DIR, 'src', 'database', 'logistica.db')}",
)

# Si es ruta relativa sqlite, hacerla absoluta respecto a BASE_DIR
if SQLALCHEMY_DATABASE_URL.startswith("sqlite:///./"):
    rel = SQLALCHEMY_DATABASE_URL.replace("sqlite:///./", "")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'src', 'database', os.path.basename(rel))}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
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
