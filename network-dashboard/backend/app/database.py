"""Database connection and models for the network dashboard."""

from datetime import datetime
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session

# Create a persistent data directory inside ``backend`` to store the DB file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'network_dashboard.db')}"

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

    # Delete orphaned port rows when they are removed from the relationship to
    # avoid NULL ``dispositivo_id`` errors when updating devices.
    puertos = relationship(
        "Puerto",
        backref="dispositivo",
        cascade="all, delete, delete-orphan",
    )

class MetricaHistorica(Base):
    __tablename__ = "metricas_historicas"

    id = Column(Integer, primary_key=True, index=True)
    dispositivo_id = Column(Integer, ForeignKey("dispositivos.id"), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    latencia_ms = Column(Float, nullable=True)
    estado = Column(String, nullable=True)  # up/down
    paquetes_perdidos = Column(Float, nullable=True)

    dispositivo = relationship("Dispositivo", backref="historico_metricas")

def crear_base_datos() -> None:
    """Crea las tablas en la base de datos si no existen."""
    Base.metadata.create_all(bind=engine)


def insertar_dispositivo(session: Session, data: dict) -> Dispositivo:
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
    session.refresh(dispositivo)
    return dispositivo


def actualizar_dispositivo(session: Session, data: dict) -> Dispositivo:
    """Actualiza un dispositivo existente, sobrescribiendo sus datos y puertos.

    Args:
        session (Session): Sesión activa de SQLAlchemy.
        data (dict): Diccionario con los datos actualizados del dispositivo.
    """
    dispositivo = session.query(Dispositivo).filter_by(ip=data["ip"]).first()
    if not dispositivo:
        dispositivo = insertar_dispositivo(session, data)
        return dispositivo

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
    session.refresh(dispositivo)
    return dispositivo


def insertar_o_actualizar_dispositivo(data: dict) -> None:
    """Inserta o actualiza un dispositivo utilizando una sesión temporal."""
    session = SessionLocal()
    try:
        actualizar_dispositivo(session, data)
    finally:
        session.close()

def guardar_metrica(session: Session, dispositivo_id: int, latencia_ms: float, paquetes_perdidos: float) -> None:
    metrica = MetricaHistorica(
        dispositivo_id=dispositivo_id,
        latencia_ms=latencia_ms,
        paquetes_perdidos=paquetes_perdidos,
        estado="up"
    )
    session.add(metrica)
    session.commit()

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "Dispositivo",
    "crear_base_datos",
    "insertar_dispositivo",
    "actualizar_dispositivo",
    "insertar_o_actualizar_dispositivo",
    "guardar_metrica",
]
