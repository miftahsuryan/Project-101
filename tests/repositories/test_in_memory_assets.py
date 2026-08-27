from uuid import uuid4

from production_app.domain.entities import Asset
from production_app.repositories.assets_repo import AssetRepository
from production_app.repositories.in_memory_assets import (
    InMemoryAssetRepository,
)


def test_add_asset_can_be_read_back() -> None:
    repository = InMemoryAssetRepository()

    asset = Asset(id=uuid4(), asset_code="PUMP-01", name="Main Pump")

    repository.add(asset)

    assert repository.get(asset.id) == asset


def test_get_missing_asset_returns_none() -> None:
    repository = InMemoryAssetRepository()

    missing_id = uuid4()

    assert repository.get(missing_id) is None


def test_get_by_code_returns_matching_asset() -> None:
    repository = InMemoryAssetRepository()

    first = Asset(
        id=uuid4(),
        asset_code="PUMP-01",
        name="Main Pump",
    )
    second = Asset(
        id=uuid4(),
        asset_code="VALVE-01",
        name="Intake Valve",
    )

    repository.add(first)
    repository.add(second)

    assert repository.get_by_code("PUMP-01") == first
    assert repository.get_by_code("VALVE-01") == second
    assert repository.get_by_code("MISSING-01") is None


def test_list_assets_applies_limit_and_offset() -> None:
    repository = InMemoryAssetRepository()

    assets = [
        Asset(
            id=uuid4(),
            asset_code=f"PUMP-{number:02}",
            name=f"Pump {number}",
        )
        for number in range(1, 4)
    ]

    for asset in assets:
        repository.add(asset)

    assert repository.list_assets() == assets
    assert (
        repository.list_assets(
            limit=2,
            offset=1,
        )
        == assets[1:3]
    )


def test_list_assets_filters_by_exact_asset_code() -> None:
    repository = InMemoryAssetRepository()

    first = Asset(
        id=uuid4(),
        asset_code="PUMP-01",
        name="Main Pump",
    )
    second = Asset(
        id=uuid4(),
        asset_code="VALVE-01",
        name="Intake Valve",
    )

    repository.add(first)
    repository.add(second)

    assert repository.list_assets(
        asset_code="PUMP-01",
    ) == [first]

    assert (
        repository.list_assets(
            asset_code="PUMP",
        )
        == []
    )

    assert (
        repository.list_assets(
            asset_code="MISSING-01",
        )
        == []
    )


def test_replace_asset_updates_primary_and_secondary_indexes() -> None:
    repository = InMemoryAssetRepository()

    original = Asset(
        id=uuid4(),
        asset_code="PUMP-01",
        name="Main Pump",
    )
    repository.add(original)

    updated = Asset(
        id=original.id,
        asset_code="PUMP-02",
        name="Backup Pump",
    )

    repository.replace(updated)

    assert repository.get(original.id) == updated

    assert repository.get_by_code("PUMP-01") is None
    assert repository.get_by_code("PUMP-02") == updated


def test_delete_asset_removes_primary_and_secondary_indexes() -> None:
    repository = InMemoryAssetRepository()

    asset = Asset(
        id=uuid4(),
        asset_code="PUMP-01",
        name="Main Pump",
    )
    repository.add(asset)

    repository.delete(asset.id)

    assert repository.get(asset.id) is None
    assert repository.get_by_code("PUMP-01") is None
    assert repository.list_assets() == []


def test_in_memory_repository_satisfies_repository_contract() -> None:
    repository: AssetRepository = InMemoryAssetRepository()

    assert repository.list_assets() == []
