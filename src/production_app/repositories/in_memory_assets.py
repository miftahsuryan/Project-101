from uuid import UUID

from production_app.domain.entities import Asset


class InMemoryAssetRepository:
    def __init__(self) -> None:
        self._assets: dict[UUID, Asset] = {}
        self._asset_ids_by_code: dict[str, UUID] = {}

    def count(self) -> int:
        return len(self._assets)

    def add(self, asset: Asset) -> None:
        self._assets[asset.id] = asset
        self._asset_ids_by_code[asset.asset_code] = asset.id

    def get(self, asset_id: UUID) -> Asset | None:
        return self._assets.get(asset_id)

    def get_by_code(
        self,
        asset_code: str,
    ) -> Asset | None:
        asset_id = self._asset_ids_by_code.get(asset_code)

        if asset_id is None:
            return None

        return self._assets.get(asset_id)

    def list_assets(
        self,
        *,
        asset_code: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Asset]:
        if asset_code is None:
            assets = list(self._assets.values())
        else:
            asset = self.get_by_code(asset_code)

            if asset is None:
                assets = []
            else:
                assets = [asset]

        stop = None if limit is None else offset + limit

        return assets[offset:stop]

    def replace(self, asset: Asset) -> None:
        current = self._assets[asset.id]

        if current.asset_code != asset.asset_code:
            del self._asset_ids_by_code[current.asset_code]

        self._assets[asset.id] = asset
        self._asset_ids_by_code[asset.asset_code] = asset.id

    def delete(self, asset_id: UUID) -> None:
        asset = self._assets.pop(asset_id)
        del self._asset_ids_by_code[asset.asset_code]
