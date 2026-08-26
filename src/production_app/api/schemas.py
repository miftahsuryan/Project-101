from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from production_app.config import Environment

AssetId = Annotated[
    str, Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")
]

AssetCode = Annotated[
    str,
    Field(
        min_length=1,
        max_length=100,
        pattern=r"^[A-Za-z0-9_-]+$",
    ),
]

AssetName = Annotated[
    str,
    Field(
        min_length=1,
        max_length=200,
    ),
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


class AssetCreate(BaseModel):
    asset_code: AssetCode
    name: AssetName


class AssetResponse(BaseModel):
    id: UUID
    asset_code: str
    name: str


class AssetUpdate(BaseModel):
    asset_code: AssetCode
    name: AssetName


class ErrorDetail(BaseModel):
    field: str
    message: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail]


class ErrorResponse(BaseModel):
    error: ErrorBody
