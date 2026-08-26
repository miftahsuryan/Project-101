class ProductionAppError(Exception):
    """Base exception for expected application errors."""


class CsvIngestionError(ProductionAppError):
    """Raised when CSV input violates the ingestion contract."""


class ConfigError(ProductionAppError):
    """Raised when application configuration is invalid."""


class PredictionUnavailableError(ProductionAppError):
    """Raised when a prediction cannot be produced."""

    def __init__(self, asset_id: str) -> None:
        self.asset_id = asset_id
        super().__init__(f"Prediction is unavailable for asset {asset_id!r}.")


class AssetNotFoundError(ProductionAppError):
    """Raised when an asset cannot be found."""

    def __init__(self, asset_id: str) -> None:
        self.asset_id = asset_id
        super().__init__(f"Asset {asset_id!r} was not found.")


class AssetCodeAlreadyExistsError(ProductionAppError):
    """Raised when an asset code is already in use."""

    def __init__(self, asset_code: str) -> None:
        self.asset_code = asset_code
        super().__init__(f"Asset code {asset_code!r} is already in use.")
