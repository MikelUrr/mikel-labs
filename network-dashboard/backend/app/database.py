"""
setup database connection andd models for networwork dashboard.
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session

DATABASE_URL = "sqlite:///network_dashboard.db"

Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


class Puerto(Base):
    """Modelo que representa un puerto abierto en un dispositivo."""
    __tablename__ = "puertos"

    id = Column(Integer, primary_key=True, index=True)
    dispositivo_id = Column(Integer, ForeignKey("dispositivos.id"), nullable=False)
    puerto = Column(Integer, nullable=False)
    estado = Column(String, nullable=False)
    servicio = Column(String, nullable=True)
    producto = Column(String, nullable=True)


class Dispositivo(Base):
    """Modelo que representa un dispositivo detectado en la red."""
    __tablename__ = "dispositivos"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, unique=True, index=True, nullable=False)
    estado = Column(String, nullable=False)
    hostname = Column(String, nullable=True)
    mac = Column(String, nullable=True)
    vendor = Column(String, nullable=True)
    detectado = Column(DateTime, default=datetime.utcnow)

    puertos = relationship("Puerto", backref="dispositivo", cascade="all, delete")


def crear_base_datos() -> None:
    """Crea las tablas en la base de datos si no existen."""
    Base.metadata.create_all(bind=engine)


def insertar_dispositivo(session: Session, data: dict) -> None:
    """Inserta un nuevo dispositivo y sus puertos en la base de datos.

    Args:
        session (Session): Sesión activa de SQLAlchemy.
        data (dict): Diccionario con los datos del dispositivo.
    """
    dispositivo = Dispositivo(
        ip=data["ip"],
        estado=data["estado"],
        hostname=data.get("hostname"),
        mac=data.get("mac"),
        vendor=data.get("vendor"),
        detectado=datetime.fromisoformat(data["detectado"])
    )

    for puerto in data.get("puertos", []):
        dispositivo.puertos.append(Puerto(
            puerto=puerto["puerto"],
            estado=puerto["estado"],
            servicio=puerto.get("servicio"),
            producto=puerto.get("producto")
        ))

    session.add(dispositivo)
    session.commit()


def actualizar_dispositivo(session: Session, data: dict) -> None:
    """Actualiza un dispositivo existente, sobrescribiendo sus datos y puertos.

    Args:
        session (Session): Sesión activa de SQLAlchemy.
        data (dict): Diccionario con los datos actualizados del dispositivo.
    """
    dispositivo = session.query(Dispositivo).filter_by(ip=data["ip"]).first()
    if not dispositivo:
        insertar_dispositivo(session, data)
        return

    dispositivo.estado = data["estado"]
    dispositivo.hostname = data.get("hostname")
    dispositivo.mac = data.get("mac")
    dispositivo.vendor = data.get("vendor")
    dispositivo.detectado = datetime.fromisoformat(data["detectado"])

    dispositivo.puertos.clear()
    for puerto in data.get("puertos", []):
        dispositivo.puertos.append(Puerto(
            puerto=puerto["puerto"],
            estado=puerto["estado"],
            servicio=puerto.get("servicio"),
            producto=puerto.get("producto")
        ))

    session.commit()



__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "Dispositivo",
    "crear_base_datos",
    "insertar_dispositivo",
    "actualizar_dispositivo",
]