from fastapi import FastAPI

from production_app.api.error_handlers import register_exception_handlers
from production_app.api.routes.assets import create_assets_router
from production_app.api.routes.health import create_health_router
from production_app.api.routes.predictions import router as predictions_router
from production_app.config import load_config
from production_app.repositories.in_memory_assets import (
    InMemoryAssetRepository,
)
from production_app.services.assets import AssetService


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    config = load_config()

    asset_repository = InMemoryAssetRepository()
    asset_service = AssetService(repository=asset_repository)

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
    app.include_router(
        create_assets_router(asset_service),
        prefix="/api/v1",
    )

    return app
