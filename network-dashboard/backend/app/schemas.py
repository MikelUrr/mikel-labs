"""Pydantic schemas for API request/response validation and documentation.

This module contains all data models used for:
- Input validation in API endpoints.
- Response serialization.
- OpenAPI/Swagger documentation.

Schemas are organized by entity type (Device, Port, Metric).
Each schema includes:
- Field definitions with types and descriptions.
- Pydantic configuration for ORM compatibility.
- Example data for API documentation.

Example:
    ```python
    # Using a schema for request validation
    device = DispositivoCreateSchema(**request.json())
    ```
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ConfigMixin:
    """Shared Pydantic configuration for all schemas."""
    class Config:
        orm_mode = True
        extra = "forbid"  # Reject extra fields
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class PuertoBase(BaseModel):
    """Base schema with common port fields."""
    puerto: int = Field(..., description="Número de puerto (1-65535)", example=80)
    estado: str = Field(..., description="Estado del puerto", example="open")


class PuertoCreateSchema(PuertoBase):
    """Schema for port creation."""
    servicio: Optional[str] = Field(
        None,
        description="Servicio detectado en el puerto",
        example="http",
    )
    producto: Optional[str] = Field(
        None,
        description="Software asociado al servicio",
        example="Apache httpd",
    )


class PuertoSchema(PuertoCreateSchema, ConfigMixin):
    """Complete port schema for responses."""
    pass


class DispositivoBase(BaseModel):
    """Base schema with common device fields."""
    ip: str = Field(..., description="Dirección IP del dispositivo", example="192.168.1.1")
    estado: str = Field(..., description="Estado del dispositivo", example="up")


class DispositivoCreateSchema(DispositivoBase):
    """Schema for device creation/update."""
    hostname: Optional[str] = Field(
        None,
        description="Nombre de host si es resoluble",
        example="router.local",
    )
    mac: Optional[str] = Field(
        None,
        description="Dirección MAC (formato AA:BB:CC:DD:EE:FF)",
        example="00:1A:2B:3C:4D:5E",
    )
    vendor: Optional[str] = Field(
        None,
        description="Fabricante derivado de la MAC",
        example="Cisco Systems",
    )
    detectado: datetime = Field(
        ...,
        description="Fecha/hora de detección",
        example="2023-01-01T00:00:00Z",
    )
    puertos: List[PuertoCreateSchema] = Field(
        [],
        description="Lista de puertos abiertos",
    )


class DispositivoSchema(DispositivoCreateSchema, ConfigMixin):
    """Complete device schema for responses."""
    id: int = Field(..., description="ID único en la base de datos", example=1)


class MetricaBase(BaseModel):
    """Base schema for historical metrics."""
    latencia_ms: Optional[float] = Field(
        None,
        description="Latencia de ping en milisegundos",
        example=5.2,
        ge=0,
    )
    paquetes_perdidos: Optional[float] = Field(
        None,
        description="Porcentaje de paquetes perdidos (0-100)",
        example=0.5,
        ge=0,
        le=100,
    )
    estado: Optional[str] = Field(
        None,
        description="Estado del dispositivo ('up' o 'down')",
        example="up",
    )


class MetricaCreateSchema(MetricaBase):
    """Schema for metric submission."""
    dispositivo_id: int = Field(..., description="ID del dispositivo relacionado", example=1)


class MetricaSchema(MetricaCreateSchema, ConfigMixin):
    """Complete metric schema for responses."""
    id: int = Field(..., description="ID único en la base de datos", example=1)
    fecha: datetime = Field(..., description="Fecha/hora de la métrica")


# Response schemas for API operations
class BulkUpdateResponse(BaseModel):
    """Schema for bulk operation responses."""
    updated: int = Field(..., description="Número de dispositivos actualizados")
    created: int = Field(..., description="Número de dispositivos creados")


__all__ = [
    "PuertoCreateSchema",
    "PuertoSchema",
    "DispositivoCreateSchema",
    "DispositivoSchema",
    "MetricaCreateSchema",
    "MetricaSchema",
    "BulkUpdateResponse",
]