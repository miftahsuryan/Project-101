from uuid import UUID, uuid4

import pytest

from production_app.exceptions import (
    AssetCodeAlreadyExistsError,
    AssetNotFoundError,
)
from production_app.services.assets import InMemoryAssetService


def test_create_asset_can_be_read_back() -> None:
    service = InMemoryAssetService()

    created = service.create_asset(
        asset_code="PUMP-01",
        name="Main Pump",
    )

    assert isinstance(created.id, UUID)
    assert created.asset_code == "PUMP-01"
    assert created.name == "Main Pump"

    stored = service.get_asset(created.id)

    assert stored == created


def test_get_asset_raises_domain_error_when_missing() -> None:
    service = InMemoryAssetService()
    missing_id = uuid4()

    with pytest.raises(
        AssetNotFoundError,
        match=str(missing_id),
    ):
        service.get_asset(missing_id)


def test_list_assets_returns_empty_list() -> None:
    service = InMemoryAssetService()

    assets = service.list_assets()

    assert assets == []


def test_list_assets_returns_creation_order() -> None:
    service = InMemoryAssetService()

    first = service.create_asset(
        asset_code="PUMP-01",
        name="Main Pump",
    )
    second = service.create_asset(
        asset_code="VALVE-01",
        name="Intake Valve",
    )

    assets = service.list_assets()

    assert assets == [first, second]


def test_create_asset_rejects_duplicate_asset_code() -> None:
    service = InMemoryAssetService()

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

    assert service.list_assets() == [original]


def test_update_asset_replaces_data_and_preserves_id() -> None:
    service = InMemoryAssetService()

    original = service.create_asset(
        asset_code="PUMP-01",
        name="Main Pump",
    )

    updated = service.update_asset(
        asset_id=original.id,
        asset_code="PUMP-02",
        name="Backup Pump",
    )

    assert updated.id == original.id
    assert updated.asset_code == "PUMP-02"
    assert updated.name == "Backup Pump"
    assert service.get_asset(original.id) == updated

    assert original.asset_code == "PUMP-01"
    assert original.name == "Main Pump"

    replacement = service.create_asset(
        asset_code="PUMP-01",
        name="Replacement Pump",
    )

    assert replacement.asset_code == "PUMP-01"


def test_update_asset_raises_domain_error_when_missing() -> None:
    service = InMemoryAssetService()
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

    assert service.list_assets() == []


def test_update_asset_rejects_code_owned_by_another_asset() -> None:
    service = InMemoryAssetService()

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

    assert service.list_assets() == [first, second]
    assert service.get_asset(second.id) == second


def test_delete_asset_removes_asset_and_releases_code() -> None:
    service = InMemoryAssetService()

    created = service.create_asset(
        asset_code="PUMP-01",
        name="Main Pump",
    )

    service.delete_asset(created.id)

    assert service.list_assets() == []

    with pytest.raises(AssetNotFoundError, match=str(created.id)):
        service.get_asset(created.id)

    replacement = service.create_asset(
        asset_code="PUMP-01",
        name="Replacement Pump",
    )

    assert replacement.asset_code == "PUMP-01"


def test_delete_asset_raises_domain_error_when_missing() -> None:
    service = InMemoryAssetService()
    missing_id = uuid4()

    with pytest.raises(
        AssetNotFoundError,
        match=str(missing_id),
    ):
        service.delete_asset(missing_id)

    assert service.list_assets() == []
