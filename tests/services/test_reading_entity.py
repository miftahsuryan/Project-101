from uuid import uuid4

from production_app.domain.entities import Reading


def test_reading_contains_asset_code_and_value() -> None:
    reading = Reading(
        id=uuid4(),
        asset_code="A-01",
        value=10.0,
    )

    assert reading.asset_code == "A-01"
    assert reading.value == 10.0
