# app/modelos/base.py
"""
Modelo base para C4A SaaS
Configuración SQLAlchemy con soporte para niveles de suscripción
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, DateTime, func
import uuid

from ..core.config import config

# Configurar motor de base de datos (síncrono para crear tablas)
url_sincrono = config.url_base_datos.replace("postgresql+asyncpg://", "postgresql://")
url_sincrono = url_sincrono.replace("localhost", "c4a_postgres")
engine = create_engine(
    url_sincrono,
    echo=config.debug,
    pool_pre_ping=True,
    pool_recycle=300
)

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

# Metadatos
metadata = MetaData()

class ModeloConUUID(Base):
    """Modelo base con UUID como clave primaria"""
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

class ModeloConEliminacionLogica(ModeloConUUID):
    """Modelo base con eliminación lógica"""
    __abstract__ = True
    
    fecha_eliminacion = Column(DateTime(timezone=True), nullable=True)

def crear_tablas():
    """Crear todas las tablas"""
    Base.metadata.create_all(bind=engine)

def obtener_sesion():
    """Obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()