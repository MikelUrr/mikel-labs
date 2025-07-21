"""Custom parameter validators for API endpoints."""

from fastapi import Depends, HTTPException
import re

#
IP_REGEX = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'

def validate_ip(ip: str) -> str:
    """Validates IPv4 address format.
    
    Args:
        ip: IP address string to validate
    
    Raises:
        HTTPException: 422 if format is invalid
    
    Returns:
        Validated IP string
    """
    if not re.match(IP_REGEX, ip):
        raise HTTPException(
            status_code=422,
            detail="Invalid IP address format (expected IPv4)"
        )
    return ip