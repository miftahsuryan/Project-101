from production_app.services.risk_baseline import (
    RiskBaselineService,
)


def test_normal_reading_has_low_risk() -> None:
    result = RiskBaselineService().predict(
        air_temperature=298.1,
        process_temperature=308.6,
        rotational_speed=1500.0,
        torque=20.0,
        tool_wear=10.0,
    )

    assert result.risk_level == "low"
    assert 0.0 <= result.risk_score <= 0.33
    assert result.model_version == "baseline-v1"


def test_extreme_reading_has_high_risk() -> None:
    result = RiskBaselineService().predict(
        air_temperature=298.1,
        process_temperature=320.0,
        rotational_speed=3000.0,
        torque=75.0,
        tool_wear=240.0,
    )

    assert result.risk_level == "high"
    assert result.risk_score > 0.66


def test_same_input_is_deterministic() -> None:
    service = RiskBaselineService()

    first = service.predict(
        air_temperature=298.1,
        process_temperature=308.6,
        rotational_speed=1551.0,
        torque=42.8,
        tool_wear=100.0,
    )
    second = service.predict(
        air_temperature=298.1,
        process_temperature=308.6,
        rotational_speed=1551.0,
        torque=42.8,
        tool_wear=100.0,
    )

    assert first == second