from fastapi import APIRouter, status

from production_app.api.schemas import HealthResponse
from production_app.config import AppConfig


def create_health_router(config: AppConfig) -> APIRouter:
    router = APIRouter()

    @router.get(
        "/health",
        response_model=HealthResponse,
        status_code=status.HTTP_200_OK,
    )
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            environment=config.environment,
        )

    return router
