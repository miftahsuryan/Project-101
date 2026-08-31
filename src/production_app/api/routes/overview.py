from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends, status

from production_app.api.schemas import OverviewResponse
from production_app.services.overview import OverviewService


def create_overview_router(
    service_dependency: Callable[..., OverviewService],
) -> APIRouter:
    router = APIRouter(
        prefix="/overview",
        tags=["overview"],
    )

    @router.get(
        "",
        response_model=OverviewResponse,
        status_code=status.HTTP_200_OK,
    )
    def get_overview(
        service: Annotated[
            OverviewService,
            Depends(service_dependency),
        ],
    ) -> OverviewResponse:
        overview = service.get_overview()

        return OverviewResponse(
            total_assets=overview.total_assets,
            total_readings=overview.total_readings,
            average_reading=overview.average_reading,
            latest_reading=overview.latest_reading,
        )

    return router
