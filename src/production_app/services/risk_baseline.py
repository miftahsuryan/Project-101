from dataclasses import dataclass


@dataclass(frozen=True)
class RiskPrediction:
    risk_score: float
    risk_level: str
    model_version: str


class RiskBaselineService:
    model_version = "baseline-v1"

    def predict(
        self,
        *,
        air_temperature: float,
        process_temperature: float,
        rotational_speed: float,
        torque: float,
        tool_wear: float,
    ) -> RiskPrediction:
        temperature_gap = max(
            process_temperature - air_temperature,
            0.0,
        )

        wear_score = min(tool_wear / 240.0, 1.0)
        torque_score = min(torque / 75.0, 1.0)
        speed_score = min(
            abs(rotational_speed - 1500.0) / 1000.0,
            1.0,
        )
        temperature_score = min(temperature_gap / 15.0, 1.0)

        score = (
            0.35 * wear_score
            + 0.30 * torque_score
            + 0.20 * speed_score
            + 0.15 * temperature_score
        )

        score = round(min(max(score, 0.0), 1.0), 4)

        if score <= 0.33:
            level = "low"
        elif score <= 0.66:
            level = "medium"
        else:
            level = "high"

        return RiskPrediction(
            risk_score=score,
            risk_level=level,
            model_version=self.model_version,
        )