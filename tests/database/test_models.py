from production_app.database.models import (
    AssetModel,
    Base,
)


def test_asset_model_maps_assets_table() -> None:
    table = Base.metadata.tables["assets"]

    assert AssetModel.__tablename__ == "assets"
    assert table.name == "assets"

    assert set(table.columns.keys()) == {
        "id",
        "asset_code",
        "name",
        "created_at",
        "updated_at",
    }

    assert table.c.id.primary_key is True
    assert table.c.asset_code.unique is True
    assert table.c.asset_code.nullable is False
    assert table.c.name.nullable is False
    assert table.c.created_at.nullable is False
    assert table.c.updated_at.nullable is False
