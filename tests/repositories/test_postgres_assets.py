from uuid import uuid4

from sqlalchemy.orm import Session

from production_app.database.models import AssetModel
from production_app.domain.entities import Asset
from production_app.repositories.postgres_assets import (
    PostgresAssetRepository,
)


def test_add_stages_asset_without_committing() -> None:
    asset = Asset(
        id=uuid4(),
        asset_code="PUMP-01",
        name="Main Pump",
    )

    with Session() as session:
        repository = PostgresAssetRepository(session)

        repository.add(asset)

        staged = next(iter(session.new))

    assert isinstance(staged, AssetModel)
    assert staged.id == asset.id
    assert staged.asset_code == asset.asset_code
    assert staged.name == asset.name
