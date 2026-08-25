from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from production_app.exceptions import PredictionUnavailableError


@dataclass(frozen=True, slots=True)
class PredictionResult:
    asset_id: str
    predicted_value: float
    model_version: Literal["fake-v1"]


def predict(
    asset_id: str,
    readings: Sequence[float],
) -> PredictionResult:
    """Return a canned prediction until a real model is available."""
    if asset_id == "A-404":
        raise PredictionUnavailableError(asset_id)

    return PredictionResult(
        asset_id=asset_id,
        predicted_value=0.0,
        model_version="fake-v1",
    )
