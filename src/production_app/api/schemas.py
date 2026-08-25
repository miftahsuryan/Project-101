from typing import Annotated, Literal

from pydantic import BaseModel, Field

from production_app.config import Environment

AssetId = Annotated[
    str, Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")
]

Readings = Annotated[
    list[float],
    Field(
        min_length=1,
        max_length=1000,
    ),
]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    environment: Environment


class PredictionRequest(BaseModel):
    asset_id: AssetId
    readings: Readings


class PredictionResponse(BaseModel):
    asset_id: str
    predicted_value: float
    model_version: Literal["fake-v1"]


class ErrorDetail(BaseModel):
    field: str
    message: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail]


class ErrorResponse(BaseModel):
    error: ErrorBody
