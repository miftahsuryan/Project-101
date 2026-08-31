from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from production_app.database.models import AssetModel
from production_app.domain.entities import Asset


def _to_domain(model: AssetModel) -> Asset:
    return Asset(
        id=model.id,
        asset_code=model.asset_code,
        name=model.name,
    )


def _to_model(asset: Asset) -> AssetModel:
    return AssetModel(
        id=asset.id,
        asset_code=asset.asset_code,
        name=asset.name,
    )


class PostgresAssetRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, asset: Asset) -> None:
        self._session.add(_to_model(asset))

    def count(self) -> int:
        statement = select(func.count(AssetModel.id))
        result = self._session.scalar(statement)
        return int(result or 0)

    def get(self, asset_id: UUID) -> Asset | None:
        model = self._session.get(AssetModel, asset_id)

        if model is None:
            return None

        return _to_domain(model)

    def get_by_code(self, asset_code: str) -> Asset | None:
        statement = select(AssetModel).where(AssetModel.asset_code == asset_code)
        model = self._session.scalar(statement)

        if model is None:
            return None

        return _to_domain(model)

    def list_assets(
        self,
        *,
        asset_code: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Asset]:
        statement = select(AssetModel).order_by(
            AssetModel.created_at,
            AssetModel.id,
        )

        if asset_code is not None:
            statement = statement.where(AssetModel.asset_code == asset_code)

        if limit is not None:
            statement = statement.limit(limit)

        statement = statement.offset(offset)

        models = self._session.scalars(statement).all()

        return [_to_domain(model) for model in models]

    def replace(self, asset: Asset) -> None:
        model = self._session.get(AssetModel, asset.id)

        if model is None:
            return

        model.asset_code = asset.asset_code
        model.name = asset.name

    def delete(self, asset_id: UUID) -> None:
        model = self._session.get(AssetModel, asset_id)

        if model is not None:
            self._session.delete(model)
