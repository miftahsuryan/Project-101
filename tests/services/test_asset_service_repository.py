from uuid import UUID, uuid4

import pytest

from production_app.domain.entities import Asset
from production_app.exceptions import (
    AssetCodeAlreadyExistsError,
    AssetNotFoundError,
)
from production_app.repositories.in_memory_assets import (
    InMemoryAssetRepository,
)
from production_app.services.assets import AssetService


def test_create_asset_stores_entity_through_repository() -> None:
    repository = InMemoryAssetRepository()
    service = AssetService(repository=repository)

    created = service.create_asset(
        asset_code="PUMP-01",
        name="Main Pump",
    )

    assert isinstance(created.id, UUID)
    assert created.asset_code == "PUMP-01"
    assert created.name == "Main Pump"

    assert repository.get(created.id) == created


def test_get_asset_returns_entity_from_repository() -> None:
    repository = InMemoryAssetRepository()
    service = AssetService(repository=repository)

    asset = Asset(
        id=uuid4(),
        asset_code="PUMP-01",
        name="Main Pump",
    )
    repository.add(asset)

    assert service.get_asset(asset.id) == asset


def test_get_asset_translates_missing_data_to_domain_error() -> None:
    repository = InMemoryAssetRepository()
    service = AssetService(repository=repository)
    missing_id = uuid4()

    with pytest.raises(
        AssetNotFoundError,
        match=str(missing_id),
    ):
        service.get_asset(missing_id)


def test_list_assets_delegates_filter_and_pagination() -> None:
    repository = InMemoryAssetRepository()
    service = AssetService(repository=repository)

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

    paginated = service.list_assets(
        limit=1,
        offset=1,
    )
    filtered = service.list_assets(
        asset_code="PUMP-03",
    )

    assert paginated == [assets[1]]
    assert filtered == [assets[2]]


def test_create_asset_rejects_duplicate_code() -> None:
    repository = InMemoryAssetRepository()
    service = AssetService(repository=repository)

    original = service.create_asset(
        asset_code="PUMP-01",
        name="Main Pump",
    )

    with pytest.raises(
        AssetCodeAlreadyExistsError,
        match="PUMP-01",
    ):
        service.create_asset(
            asset_code="PUMP-01",
            name="Duplicate Pump",
        )

    assert repository.list_assets() == [original]


def test_update_asset_replaces_entity_and_preserves_id() -> None:
    repository = InMemoryAssetRepository()
    service = AssetService(repository=repository)

    original = service.create_asset(
        asset_code="PUMP-01",
        name="Main Pump",
    )

    updated = service.update_asset(
        asset_id=original.id,
        asset_code="PUMP-02",
        name="Backup Pump",
    )

    assert updated == Asset(
        id=original.id,
        asset_code="PUMP-02",
        name="Backup Pump",
    )

    assert repository.get(original.id) == updated
    assert repository.get_by_code("PUMP-01") is None
    assert repository.get_by_code("PUMP-02") == updated


def test_update_asset_raises_domain_error_when_missing() -> None:
    repository = InMemoryAssetRepository()
    service = AssetService(repository=repository)
    missing_id = uuid4()

    with pytest.raises(
        AssetNotFoundError,
        match=str(missing_id),
    ):
        service.update_asset(
            asset_id=missing_id,
            asset_code="PUMP-01",
            name="Missing Pump",
        )

    assert repository.list_assets() == []


def test_update_asset_rejects_code_owned_by_another_asset() -> None:
    repository = InMemoryAssetRepository()
    service = AssetService(repository=repository)

    first = service.create_asset(
        asset_code="PUMP-01",
        name="Main Pump",
    )
    second = service.create_asset(
        asset_code="VALVE-01",
        name="Intake Valve",
    )

    with pytest.raises(
        AssetCodeAlreadyExistsError,
        match="PUMP-01",
    ):
        service.update_asset(
            asset_id=second.id,
            asset_code="PUMP-01",
            name="Duplicate Pump",
        )

    assert repository.list_assets() == [first, second]
    assert repository.get(second.id) == second
    assert repository.get_by_code("VALVE-01") == second


def test_delete_asset_removes_entity_and_releases_code() -> None:
    repository = InMemoryAssetRepository()
    service = AssetService(repository=repository)

    created = service.create_asset(
        asset_code="PUMP-01",
        name="Main Pump",
    )

    service.delete_asset(created.id)

    assert repository.get(created.id) is None
    assert repository.get_by_code("PUMP-01") is None
    assert repository.list_assets() == []

    replacement = service.create_asset(
        asset_code="PUMP-01",
        name="Replacement Pump",
    )

    assert replacement.asset_code == "PUMP-01"
