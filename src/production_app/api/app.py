from fastapi import FastAPI

from production_app.api.error_handlers import register_exception_handlers
from production_app.api.routes.health import create_health_router
from production_app.api.routes.predictions import router as predictions_router
from production_app.config import load_config


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    config = load_config()

    app = FastAPI(
        title="Production App API",
        version="0.1.0",
    )
    register_exception_handlers(app)

    app.include_router(
        create_health_router(config),
        prefix="/api/v1",
    )

    app.include_router(
        predictions_router,
        prefix="/api/v1",
    )

    return app
