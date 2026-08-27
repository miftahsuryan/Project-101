from typing import Protocol
from uuid import UUID

from production_app.domain.entities import Asset


class AssetRepository(Protocol):
    def add(self, asset: Asset) -> None: ...

    def get(self, asset_id: UUID) -> Asset | None: ...

    def get_by_code(
        self,
        asset_code: str,
    ) -> Asset | None: ...

    def list_assets(
        self,
        *,
        asset_code: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Asset]: ...

    def replace(self, asset: Asset) -> None: ...

    def delete(self, asset_id: UUID) -> None: ...
