from uuid import UUID, uuid4

from production_app.domain.entities import Asset
from production_app.exceptions import (
    AssetCodeAlreadyExistsError,
    AssetNotFoundError,
)


class InMemoryAssetService:
    def __init__(self) -> None:
        self._assets: dict[UUID, Asset] = {}
        self._asset_ids_by_code: dict[str, UUID] = {}

    def create_asset(
        self,
        asset_code: str,
        name: str,
    ) -> Asset:
        if asset_code in self._asset_ids_by_code:
            raise AssetCodeAlreadyExistsError(asset_code)

        asset = Asset(
            id=uuid4(),
            asset_code=asset_code,
            name=name,
        )
        self._assets[asset.id] = asset
        self._asset_ids_by_code[asset.asset_code] = asset.id

        return asset

    def get_asset(self, asset_id: UUID) -> Asset:
        try:
            return self._assets[asset_id]
        except KeyError as error:
            raise AssetNotFoundError(str(asset_id)) from error

    def list_assets(self) -> list[Asset]:
        return list(self._assets.values())

    def update_asset(
        self,
        asset_id: UUID,
        asset_code: str,
        name: str,
    ) -> Asset:

        current = self.get_asset(asset_id)

        existing_id = self._asset_ids_by_code.get(asset_code)

        if existing_id is not None and existing_id != asset_id:
            raise AssetCodeAlreadyExistsError(asset_code)

        updated = Asset(
            id=current.id,
            asset_code=asset_code,
            name=name,
        )

        if current.asset_code != updated.asset_code:
            del self._asset_ids_by_code[current.asset_code]
            self._asset_ids_by_code[updated.asset_code] = updated.id

        self._assets[updated.id] = updated

        return updated

    def delete_asset(self, asset_id: UUID) -> None:
        asset = self.get_asset(asset_id)

        del self._asset_ids_by_code[asset.asset_code]
        del self._assets[asset.id]
