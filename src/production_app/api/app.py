from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from production_app.api.error_handlers import register_exception_handlers
from production_app.api.routes.assets import create_assets_router
from production_app.api.routes.health import create_health_router
from production_app.api.routes.predictions import router as predictions_router
from production_app.config import AppConfig, load_config
from production_app.database.schema import ensure_asset_table
from production_app.repositories.assets_repo import AssetRepository
from production_app.repositories.in_memory_assets import (
    InMemoryAssetRepository,
)
from production_app.repositories.postgres_assets import (
    PostgresAssetRepository,
)
from production_app.services.assets import AssetService


def _create_asset_repository(
    config: AppConfig,
) -> AssetRepository:
    if config.environment == "test" or config.database_url is None:
        return InMemoryAssetRepository()

    ensure_asset_table(config.database_url)

    return PostgresAssetRepository(config.database_url)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    config = load_config()

    asset_repository = _create_asset_repository(config)
    asset_service = AssetService(repository=asset_repository)

    app = FastAPI(
        title="Production App API",
        version="0.1.0",
    )
    register_exception_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_methods=[
            "GET",
            "POST",
            "PUT",
            "DELETE",
        ],
        allow_headers=[
            "Content-Type",
        ],
    )

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
