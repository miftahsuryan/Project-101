from uuid import UUID, uuid4

from production_app.domain.entities import Asset
from production_app.exceptions import (
    AssetCodeAlreadyExistsError,
    AssetNotFoundError,
)
from production_app.repositories.assets_repo import AssetRepository


class AssetService:
    def __init__(
        self,
        repository: AssetRepository,
    ) -> None:
        self._repository = repository

    def create_asset(
        self,
        asset_code: str,
        name: str,
    ) -> Asset:
        existing = self._repository.get_by_code(asset_code)

        if existing is not None:
            raise AssetCodeAlreadyExistsError(asset_code)

        asset = Asset(
            id=uuid4(),
            asset_code=asset_code,
            name=name,
        )

        self._repository.add(asset)

        return asset

    def get_asset(self, asset_id: UUID) -> Asset:
        asset = self._repository.get(asset_id)

        if asset is None:
            raise AssetNotFoundError(str(asset_id))

        return asset

    def list_assets(
        self,
        *,
        asset_code: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Asset]:
        return self._repository.list_assets(
            asset_code=asset_code,
            limit=limit,
            offset=offset,
        )

    def update_asset(
        self,
        asset_id: UUID,
        asset_code: str,
        name: str,
    ) -> Asset:
        current = self.get_asset(asset_id)

        existing = self._repository.get_by_code(asset_code)

        if existing is not None and existing.id != current.id:
            raise AssetCodeAlreadyExistsError(asset_code)

        updated = Asset(
            id=current.id,
            asset_code=asset_code,
            name=name,
        )

        self._repository.replace(updated)

        return updated

    def delete_asset(self, asset_id: UUID) -> None:
        self.get_asset(asset_id)
        self._repository.delete(asset_id)
