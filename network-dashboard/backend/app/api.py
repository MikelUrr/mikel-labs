"""API endpoints for the network dashboard.

Provides routes to retrieve port scanning information from the database.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from sqlalchemy.orm import Session
from app.database import SessionLocal, Dispositivo

router = APIRouter()

def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/puertos", response_model=List[Dict])
def get_puertos(db: Session = Depends(get_db)) -> List[Dict]:
    """Returns a list of all devices with their open ports.

    Args:
        db (Session): SQLAlchemy database session.

    Returns:
        List[Dict]: List of devices and their port information.
    """
    dispositivos = db.query(Dispositivo).all()
    resultado = []
    for d in dispositivos:
        resultado.append({
            "ip": d.ip,
            "hostname": d.hostname,
            "mac": d.mac,
            "vendor": d.vendor,
            "puertos": [{
                "puerto": p.puerto,
                "estado": p.estado,
                "servicio": p.servicio,
                "producto": p.producto
            } for p in d.puertos],
            "detectado": d.detectado.isoformat()
        })
    return resultado

@router.get("/puerto/{ip}", response_model=Dict)
def get_puerto_por_ip(ip: str, db: Session = Depends(get_db)) -> Dict:
    """Returns device and port info for a specific IP.

    Args:
        ip (str): IP address of the device.
        db (Session): SQLAlchemy session.

    Returns:
        Dict: Device data and open ports.
    """
    dispositivo = db.query(Dispositivo).filter_by(ip=ip).first()
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")

    return {
        "ip": dispositivo.ip,
        "hostname": dispositivo.hostname,
        "mac": dispositivo.mac,
        "vendor": dispositivo.vendor,
        "puertos": [{
            "puerto": p.puerto,
            "estado": p.estado,
            "servicio": p.servicio,
            "producto": p.producto
        } for p in dispositivo.puertos],
        "detectado": dispositivo.detectado.isoformat()
    }
