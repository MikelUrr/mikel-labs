"""API endpoints for the network dashboard.

Provides routes to retrieve port scanning information from the database.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import Dispositivo, SessionLocal
from app.schemas import DispositivoModel
from app.schemas import MetricaHistoricaSchema
from app.database import MetricaHistorica

router = APIRouter()

def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/puertos", response_model=List[DispositivoModel])
def get_puertos(db: Session = Depends(get_db)) -> List[DispositivoModel]:
    """Retrieve all devices with their open ports.

    Args:
        db: SQLAlchemy database session dependency.

    Returns:
        A list of devices retrieved from the database.
    """
    dispositivos = db.query(Dispositivo).all()
    return dispositivos

@router.get("/puerto/{ip}", response_model=DispositivoModel)
def get_puerto_por_ip(ip: str, db: Session = Depends(get_db)) -> DispositivoModel:
    """Retrieve device information for a specific IP.

    Args:
        ip: IP address of the device.
        db: SQLAlchemy database session dependency.

    Returns:
        The requested device or raises ``HTTPException`` if not found.
    """
    dispositivo = db.query(Dispositivo).filter_by(ip=ip).first()
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")

    return dispositivo

@router.get("/historico/{ip}", response_model=List[MetricaHistoricaSchema])
def get_historico_por_ip(ip: str, db: Session = Depends(get_db)):
    dispositivo = db.query(Dispositivo).filter_by(ip=ip).first()
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")

    return db.query(MetricaHistorica).filter_by(dispositivo_id=dispositivo.id).order_by(MetricaHistorica.fecha.desc()).all()

