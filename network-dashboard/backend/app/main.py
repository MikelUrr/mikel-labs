"""Main entry point for the FastAPI application.

This module handles:
- Network scanning with Nmap.
- API route and port configuration.
- Error logging.
- Database setup.
- Application startup.

Example:
    To run the application:
    ```bash
    sudo env "PATH=$VIRTUAL_ENV/bin:$PATH" python3 -m app.main
    ```

Attributes:
    APP_NAME (str): The name of the FastAPI application.
    API_PREFIX (str): The prefix for all API routes.

Author:
    Mikel Urrestarazu - Julio 2025
"""

import os
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn

from app.api import router as api_router
from app.database import crear_base_datos
from app.scanner import escaneo_completo

# Logging configuration
import logging
from logging.config import dictConfig

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.getenv("LOG_LEVEL", "INFO"),
    },
}

dictConfig(LOG_CONFIG)
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration
APP_NAME = "NetworkDashboard"
API_PREFIX = "/api"


def setup_api() -> FastAPI:
    """Initializes and configures the FastAPI application.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    application = FastAPI(title=APP_NAME)
    application.include_router(api_router, prefix=API_PREFIX)
    return application


def setup_scheduler() -> BackgroundScheduler:
    """Configures and starts the background scheduler.
    
    Returns:
        BackgroundScheduler: The configured scheduler instance.
    
    Raises:
        RuntimeError: If the scheduler fails to start.
    """
    scheduler = BackgroundScheduler()
    try:
        scheduler.add_job(
            escaneo_completo,
            "interval",
            seconds=int(os.getenv("SCAN_INTERVAL", "300")),
        )
        scheduler.start()
        return scheduler
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        raise RuntimeError("Scheduler failed to start") from e


def init_app() -> None:
    """Initializes the application components."""
    crear_base_datos()
    setup_scheduler()


def start(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Starts the FastAPI server.
    
    Args:
        host: The host address to bind to.
        port: The port to run the server on.
    
    Raises:
        RuntimeError: If the server fails to start.
    """
    try:
        uvicorn.run("app.main:app", host=host, port=port, reload=True)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise RuntimeError("Server failed to start") from e


app = setup_api()

if __name__ == "__main__":
    init_app()
    start()