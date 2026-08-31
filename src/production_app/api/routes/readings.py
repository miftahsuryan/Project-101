from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from production_app.api.schemas import (
    ReadingListResponse,
    ReadingResponse,
)
from production_app.services.readings import ReadingService


def create_readings_router(
    service_dependency: Callable[..., ReadingService],
) -> APIRouter:
    router = APIRouter(
        prefix="/readings",
        tags=["readings"],
    )

    @router.get(
        "",
        response_model=ReadingListResponse,
        status_code=status.HTTP_200_OK,
    )
    def list_readings(
        asset_code: str | None = None,
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
        offset: Annotated[int, Query(ge=0)] = 0,
        service: Annotated[
            ReadingService,
            Depends(service_dependency),
        ] = None,  # type: ignore[assignment]
    ) -> ReadingListResponse:
        page = service.list_readings(
            asset_code=asset_code,
            limit=limit,
            offset=offset,
        )

        return ReadingListResponse(
            items=[
                ReadingResponse(
                    id=reading.id,
                    asset_code=reading.asset_code,
                    value=reading.value,
                )
                for reading in page.items
            ],
            limit=limit,
            offset=offset,
            total=page.total,
        )

    return router