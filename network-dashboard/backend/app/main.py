"""Main entry point for the FastAPI application.

- Escaneo de red con Nmap.
- Configuración de rutas y puertos.
- Logging de errores.
- Configuración de la base de datos.
- Inicio de la aplicación.

Autor: Mikel Urrestarazu
Julio 2025
"""

import os
import uvicorn
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from app.api import router as api_router
from app.scanner import escaneo_completo
from dotenv import load_dotenv
load_dotenv()

# Configuration variables
APP_NAME = "NetworkDashboard"
API_PREFIX = "/api"


def setup_api() -> FastAPI:
    """Initializes and configures the FastAPI application.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    app = FastAPI(title=APP_NAME)
    app.include_router(api_router, prefix=API_PREFIX)
    return app


app = setup_api()

# Scheduler setup
scheduler = BackgroundScheduler()
scheduler.add_job(escaneo_completo, "interval", seconds=int(os.getenv("SCAN_INTERVAL", 300)))
scheduler.start()


def start() -> None:
    """Starts the FastAPI server with default or environment settings."""
    port = int(os.getenv("PORT", "8000"))
    host: str = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    start()
