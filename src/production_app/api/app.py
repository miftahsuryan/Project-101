from fastapi import FastAPI

from production_app.api.routes.health import create_health_router
from production_app.config import load_config


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    config = load_config()

    app = FastAPI(
        title="Production App API",
        version="0.1.0",
    )
    app.include_router(
        create_health_router(config),
        prefix="/api/v1",
    )

    return app
