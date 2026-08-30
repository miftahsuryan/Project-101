from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from production_app.api.schemas import (
    ErrorBody,
    ErrorDetail,
    ErrorResponse,
)
from production_app.exceptions import (
    AssetCodeAlreadyExistsError,
    AssetNotFoundError,
    PredictionUnavailableError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(
        _request: Request,
        error: RequestValidationError,
    ) -> JSONResponse:
        details = [
            ErrorDetail(
                field=".".join(str(part) for part in issue["loc"] if part != "body"),
                message=issue["msg"],
            )
            for issue in error.errors()
        ]

        response = ErrorResponse(
            error=ErrorBody(
                code="validation_error",
                message="Request validation failed.",
                details=details,
            )
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response.model_dump(),
        )

    @app.exception_handler(PredictionUnavailableError)
    async def handle_prediction_unavailable_error(
        _request: Request,
        error: PredictionUnavailableError,
    ) -> JSONResponse:
        response = ErrorResponse(
            error=ErrorBody(
                code="prediction_unavailable",
                message=str(error),
                details=[],
            )
        )

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=response.model_dump(),
        )

    @app.exception_handler(AssetNotFoundError)
    async def handle_asset_not_found_error(
        _request: Request,
        error: AssetNotFoundError,
    ) -> JSONResponse:
        response = ErrorResponse(
            error=ErrorBody(
                code="asset_not_found",
                message=str(error),
                details=[],
            )
        )

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=response.model_dump(),
        )

    @app.exception_handler(AssetCodeAlreadyExistsError)
    async def handle_asset_code_conflict(
        _request: Request,
        error: AssetCodeAlreadyExistsError,
    ) -> JSONResponse:
        response = ErrorResponse(
            error=ErrorBody(
                code="asset_code_conflict",
                message=str(error),
                details=[],
            )
        )

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=response.model_dump(),
        )
