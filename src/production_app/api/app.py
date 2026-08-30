from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from production_app.api.error_handlers import register_exception_handlers
from production_app.api.routes.assets import create_assets_router
from production_app.api.routes.health import create_health_router
from production_app.api.routes.predictions import router as predictions_router
from production_app.config import AppConfig, load_config
from production_app.database.session import (
    create_database_engine,
    create_session_dependency,
    create_session_factory,
)
from production_app.repositories.in_memory_assets import (
    InMemoryAssetRepository,
)
from production_app.repositories.postgres_assets import (
    PostgresAssetRepository,
)
from production_app.services.assets import AssetService


def _create_asset_service_dependency(
    config: AppConfig,
) -> Callable[..., AssetService]:
    if config.environment == "test" or config.database_url is None:
        service = AssetService(
            repository=InMemoryAssetRepository(),
        )

        def get_in_memory_service() -> AssetService:
            return service

        return get_in_memory_service

    engine = create_database_engine(config.database_url)
    session_factory = create_session_factory(engine)
    get_session = create_session_dependency(session_factory)

    def get_postgres_service(
        session: Annotated[Session, Depends(get_session)],
    ) -> AssetService:
        return AssetService(
            repository=PostgresAssetRepository(session),
        )

    return get_postgres_service


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    config = load_config()

    asset_service_dependency = _create_asset_service_dependency(config)

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
        create_assets_router(asset_service_dependency),
        prefix="/api/v1",
    )

    return app
