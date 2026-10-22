import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Si DATABASE_URL no está definida o se quiere probar localmente, usa SQLite por defecto
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Generador de sesiones de base de datos por petición."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

