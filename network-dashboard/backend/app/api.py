"""API endpoints for the Network Dashboard application.

This module provides RESTful endpoints to:
- Retrieve network devices and their open ports
- Access historical metrics
- Search/filter devices by various criteria

Routes are organized by resource type:
- /devices: Device-related operations
- /metrics: Historical data access

All endpoints:
- Return validated data using Pydantic models
- Include proper error handling (404, 422, etc.)
- Are documented in the OpenAPI schema
"""

from datetime import datetime 
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import Dispositivo, MetricaHistorica, get_db
from app.schemas import DispositivoSchema, MetricaSchema
from app.validators import validate_ip

router = APIRouter(
    prefix="/v1",
    tags=["devices"],
)


@router.get(
    "/devices",
    response_model=List[DispositivoSchema],
    summary="List all devices",
    description="Retrieves all network devices with their open ports",
)
async def list_devices(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, le=1000, description="Max items to return"),
) -> List[DispositivoSchema]:
    """Retrieves a paginated list of network devices.
    
    Args:
        db: Database session dependency.
        skip: Number of items to skip (for pagination).
        limit: Maximum number of items to return.
    
    Returns:
        List of devices with their associated ports.
    """
    return db.query(Dispositivo).offset(skip).limit(limit).all()


@router.get(
    "/devices/{ip}",
    response_model=DispositivoSchema,
    responses={
        404: {"description": "Device not found"},
        422: {"description": "Invalid IP address format"},
    },
)
async def get_device(
    ip: str = Depends(validate_ip),
    db: Session = Depends(get_db),
) -> DispositivoSchema:
    """Retrieves a single device by its IP address.
    
    Args:
        ip: Validated IP address.
        db: Database session dependency.
    
    Raises:
        HTTPException: 404 if device not found.
    
    Returns:
        The requested device with its ports.
    """
    device = db.query(Dispositivo).filter_by(ip=ip).first()
    if not device:
        raise HTTPException(
            status_code=404,
            detail=f"Device with IP {ip} not found"
        )
    return device


@router.get(
    "/devices/{ip}/metrics",
    response_model=List[MetricaSchema],
    summary="Get device metrics",
    responses={
        404: {"description": "Device not found"},
        422: {"description": "Invalid IP address format"},
    },
)
async def get_device_metrics(
    ip: str = Depends(validate_ip),
    db: Session = Depends(get_db),
    time_from: Optional[datetime] = Query(
        None,
        description="Filter metrics after this timestamp",
    ),
    time_to: Optional[datetime] = Query(
        None,
        description="Filter metrics before this timestamp",
    ),
) -> List[MetricaSchema]:
    """Retrieves historical metrics for a specific device.
    
    Args:
        ip: Validated IP address.
        db: Database session dependency.
        time_from: Optional start time filter.
        time_to: Optional end time filter.
    
    Returns:
        Chronologically ordered list of metrics.
    """
    device = db.query(Dispositivo).filter_by(ip=ip).first()
    if not device:
        raise HTTPException(
            status_code=404,
            detail=f"Device with IP {ip} not found"
        )

    query = db.query(MetricaHistorica).filter_by(dispositivo_id=device.id)
    
    if time_from:
        query = query.filter(MetricaHistorica.fecha >= time_from)
    if time_to:
        query = query.filter(MetricaHistorica.fecha <= time_to)
    
    return query.order_by(MetricaHistorica.fecha.desc()).all()


# Additional helper file: validators.py
"""
from fastapi import Depends, HTTPException
import re

IP_REGEX = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"

def validate_ip(ip: str) -> str:
    if not re.match(IP_REGEX, ip):
        raise HTTPException(
            status_code=422,
            detail="Invalid IP address format"
        )
    return ip
"""