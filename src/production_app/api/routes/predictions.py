from fastapi import APIRouter, status

from production_app.api.schemas import (
    ErrorResponse,
    PredictionRequest,
    PredictionResponse,
)
from production_app.services.predictions import predict

router = APIRouter()


@router.post(
    "/predictions",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "Prediction is unavailable.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorResponse,
            "description": "Request validation failed.",
        },
    },
)
def create_prediction(
    request: PredictionRequest,
) -> PredictionResponse:
    result = predict(
        asset_id=request.asset_id,
        readings=request.readings,
    )

    return PredictionResponse(
        asset_id=result.asset_id,
        predicted_value=result.predicted_value,
        model_version=result.model_version,
    )
