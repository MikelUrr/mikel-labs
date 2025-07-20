"""Pydantic models used by the API for documentation and validation."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class PuertoModel(BaseModel):
    """Datos de un puerto abierto en un dispositivo."""

    puerto: int
    estado: str
    servicio: Optional[str] = None
    producto: Optional[str] = None

    class Config:
        """Configuración de Pydantic."""

        orm_mode = True


class DispositivoModel(BaseModel):
    """Información de un dispositivo de red."""

    ip: str
    hostname: Optional[str] = None
    mac: Optional[str] = None
    vendor: Optional[str] = None
    detectado: datetime
    puertos: List[PuertoModel] = []

    class Config:
        """Configuración de Pydantic."""

        orm_mode = True


class MetricaHistoricaSchema(BaseModel):
    fecha: datetime
    latencia_ms: Optional[float]
    paquetes_perdidos: Optional[float]
    estado: Optional[str]

    class Config:
        orm_mode = True


__all__ = [
    "PuertoModel",
    "DispositivoModel",
    "MetricaHistoricaSchema",
]
