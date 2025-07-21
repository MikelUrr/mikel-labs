"""Database connection and models for the network dashboard.

This module handles:
- SQLite database configuration.
- SQLAlchemy model definitions.
- CRUD operations for network devices and metrics.

Example:
    To create the database tables:
    ```python
    from app.database import crear_base_datos
    crear_base_datos()
    ```

Attributes:
    DATABASE_URL (str): The connection URL for the SQLite database.
    Base: SQLAlchemy declarative base class.
    engine: SQLAlchemy engine instance.
    SessionLocal: SQLAlchemy session factory.
"""

import os
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, List, Optional, Any, Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'network_dashboard.db')}"
Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@contextmanager
def get_db() -> Iterator[Session]:
    """Yields a database session with automatic cleanup.
    
    Example:
        ```python
        with get_db() as db:
            db.query(Dispositivo).all()
        ```
    
    Yields:
        Session: SQLAlchemy database session.
    
    Raises:
        Exception: If the session cannot be created or committed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Puerto(Base):
    """Represents an open port on a network device.

    Attributes:
        id (int): Primary key.
        dispositivo_id (int): Foreign key to Dispositivo.
        puerto (int): Port number.
        estado (str): Port state (e.g., 'open', 'closed').
        servicio (Optional[str]): Service running on the port.
        producto (Optional[str]): Product name (e.g., 'Apache httpd').
    """

    __tablename__ = "puertos"

    id = Column(Integer, primary_key=True, index=True)
    dispositivo_id = Column(Integer, ForeignKey("dispositivos.id"), nullable=False)
    puerto = Column(Integer, nullable=False)
    estado = Column(String, nullable=False)
    servicio = Column(String, nullable=True)
    producto = Column(String, nullable=True)


class Dispositivo(Base):
    """Represents a network device detected in scans.

    Attributes:
        id (int): Primary key.
        ip (str): IP address (unique).
        estado (str): Device state (e.g., 'up', 'down').
        hostname (Optional[str]): Hostname if resolvable.
        mac (Optional[str]): MAC address.
        vendor (Optional[str]): Vendor derived from MAC.
        detectado (DateTime): First detection timestamp.
        puertos (List[Puerto]): List of open ports.
    """

    __tablename__ = "dispositivos"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, unique=True, index=True, nullable=False)
    estado = Column(String, nullable=False)
    hostname = Column(String, nullable=True)
    mac = Column(String, nullable=True)
    vendor = Column(String, nullable=True)
    detectado = Column(DateTime, default=datetime.utcnow)

    puertos = relationship(
        "Puerto",
        backref="dispositivo",
        cascade="all, delete, delete-orphan",
    )


class MetricaHistorica(Base):
    """Stores historical metrics for network devices.

    Attributes:
        id (int): Primary key.
        dispositivo_id (int): Foreign key to Dispositivo.
        fecha (DateTime): Metric timestamp.
        latencia_ms (Optional[float]): Ping latency in ms.
        estado (Optional[str]): Device state at time of metric.
        paquetes_perdidos (Optional[float]): Packet loss percentage.
    """

    __tablename__ = "metricas_historicas"

    id = Column(Integer, primary_key=True, index=True)
    dispositivo_id = Column(Integer, ForeignKey("dispositivos.id"), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    latencia_ms = Column(Float, nullable=True)
    estado = Column(String, nullable=True)  # 'up' or 'down'
    paquetes_perdidos = Column(Float, nullable=True)

    dispositivo = relationship("Dispositivo", backref="historico_metricas")


def crear_base_datos() -> None:
    """Creates all database tables if they don't exist."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")


def insertar_dispositivo(session: Session, data: Dict[str, Any]) -> Dispositivo:
    """Inserts a new device and its ports into the database.

    Args:
        session: SQLAlchemy session.
        data: Device data including ports.

    Returns:
        Dispositivo: The created device.

    Raises:
        ValueError: If required fields are missing.
    """
    required_fields = {"ip", "estado", "detectado"}
    if not all(field in data for field in required_fields):
        raise ValueError(f"Missing required fields: {required_fields}")

    dispositivo = Dispositivo(
        ip=data["ip"],
        estado=data["estado"],
        hostname=data.get("hostname"),
        mac=data.get("mac"),
        vendor=data.get("vendor"),
        detectado=datetime.fromisoformat(data["detectado"]),
    )

    for puerto in data.get("puertos", []):
        dispositivo.puertos.append(Puerto(
            puerto=puerto["puerto"],
            estado=puerto["estado"],
            servicio=puerto.get("servicio"),
            producto=puerto.get("producto"),
        ))

    session.add(dispositivo)
    session.commit()
    session.refresh(dispositivo)
    return dispositivo


def actualizar_dispositivo(session: Session, data: Dict[str, Any]) -> Dispositivo:
    """Updates an existing device, overwriting its ports.

    Args:
        session: SQLAlchemy session.
        data: Updated device data.

    Returns:
        Dispositivo: The updated device.

    Raises:
        ValueError: If the device does not exist and cannot be created.
    """
    dispositivo = session.query(Dispositivo).filter_by(ip=data["ip"]).first()
    if not dispositivo:
        return insertar_dispositivo(session, data)

    dispositivo.estado = data["estado"]
    dispositivo.hostname = data.get("hostname")
    dispositivo.mac = data.get("mac")
    dispositivo.vendor = data.get("vendor")
    dispositivo.detectado = datetime.fromisoformat(data["detectado"])

    # Clear existing ports and add new ones
    dispositivo.puertos.clear()
    for puerto in data.get("puertos", []):
        dispositivo.puertos.append(Puerto(
            puerto=puerto["puerto"],
            estado=puerto["estado"],
            servicio=puerto.get("servicio"),
            producto=puerto.get("producto"),
        ))

    session.commit()
    session.refresh(dispositivo)
    return dispositivo


def insertar_o_actualizar_dispositivo(data: Dict[str, Any]) -> None:
    """Inserts or updates a device using a temporary session.

    Args:
        data: Device data to insert/update.
    """
    with get_db() as db:
        actualizar_dispositivo(db, data)


def guardar_metrica(
    session: Session,
    dispositivo_id: int,
    latencia_ms: Optional[float] = None,
    paquetes_perdidos: Optional[float] = None,
) -> None:
    """Saves a historical metric for a device.

    Args:
        session: SQLAlchemy session.
        dispositivo_id: ID of the target device.
        latencia_ms: Ping latency in milliseconds.
        paquetes_perdidos: Packet loss percentage.
    """
    metrica = MetricaHistorica(
        dispositivo_id=dispositivo_id,
        latencia_ms=latencia_ms,
        paquetes_perdidos=paquetes_perdidos,
        estado="up" if latencia_ms is not None else "down",
    )
    session.add(metrica)
    session.commit()


__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "Dispositivo",
    "Puerto",
    "MetricaHistorica",
    "crear_base_datos",
    "insertar_dispositivo",
    "actualizar_dispositivo",
    "insertar_o_actualizar_dispositivo",
    "guardar_metrica",
]