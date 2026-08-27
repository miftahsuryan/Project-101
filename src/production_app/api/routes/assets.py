from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Response, status

from production_app.api.schemas import (
    AssetCreate,
    AssetResponse,
    AssetUpdate,
    ErrorResponse,
)
from production_app.domain.entities import Asset
from production_app.services.assets import AssetService


def _to_response(asset: Asset) -> AssetResponse:
    return AssetResponse(
        id=asset.id,
        asset_code=asset.asset_code,
        name=asset.name,
    )


def create_assets_router(service: AssetService) -> APIRouter:
    router = APIRouter(
        prefix="/assets",
        tags=["assets"],
    )

    @router.post(
        "",
        response_model=AssetResponse,
        status_code=status.HTTP_201_CREATED,
        responses={
            status.HTTP_409_CONFLICT: {
                "model": ErrorResponse,
                "description": "Asset code is already in use.",
            },
            status.HTTP_422_UNPROCESSABLE_CONTENT: {
                "model": ErrorResponse,
                "description": "Request validation failed.",
            },
        },
    )
    def create_asset(request: AssetCreate) -> AssetResponse:
        asset = service.create_asset(
            asset_code=request.asset_code,
            name=request.name,
        )
        return _to_response(asset)

    @router.get(
        "",
        response_model=list[AssetResponse],
        status_code=status.HTTP_200_OK,
        responses={
            status.HTTP_422_UNPROCESSABLE_CONTENT: {
                "model": ErrorResponse,
                "description": "Pagination parameters are invalid.",
            },
        },
    )
    def list_assets(
        asset_code: str | None = None,
        limit: Annotated[
            int,
            Query(ge=1, le=100),
        ] = 20,
        offset: Annotated[
            int,
            Query(ge=0),
        ] = 0,
    ) -> list[AssetResponse]:
        assets = service.list_assets(
            asset_code=asset_code,
            limit=limit,
            offset=offset,
        )

        return [_to_response(asset) for asset in assets]

    @router.get(
        "/{asset_id}",
        response_model=AssetResponse,
        status_code=status.HTTP_200_OK,
        responses={
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorResponse,
                "description": "Asset was not found.",
            },
            status.HTTP_422_UNPROCESSABLE_CONTENT: {
                "model": ErrorResponse,
                "description": "Asset ID is invalid.",
            },
        },
    )
    def get_asset(asset_id: UUID) -> AssetResponse:
        asset = service.get_asset(asset_id)
        return _to_response(asset)

    @router.put(
        "/{asset_id}",
        response_model=AssetResponse,
        status_code=status.HTTP_200_OK,
        responses={
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorResponse,
                "description": "Asset was not found.",
            },
            status.HTTP_422_UNPROCESSABLE_CONTENT: {
                "model": ErrorResponse,
                "description": "Request or asset ID is invalid.",
            },
            status.HTTP_409_CONFLICT: {
                "model": ErrorResponse,
                "description": "Asset code is already in use.",
            },
        },
    )
    def update_asset(
        asset_id: UUID,
        request: AssetUpdate,
    ) -> AssetResponse:
        asset = service.update_asset(
            asset_id=asset_id,
            asset_code=request.asset_code,
            name=request.name,
        )
        return _to_response(asset)

    @router.delete(
        "/{asset_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        response_class=Response,
        responses={
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorResponse,
                "description": "Asset was not found.",
            },
            status.HTTP_422_UNPROCESSABLE_CONTENT: {
                "model": ErrorResponse,
                "description": "Asset ID is invalid.",
            },
        },
    )
    def delete_asset(asset_id: UUID) -> Response:
        service.delete_asset(asset_id)

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router
