class ProductionAppError(Exception):
    """Base exception for expected application errors."""


class CsvIngestionError(ProductionAppError):
    """Raised when CSV input violates the ingestion contract."""


class ConfigError(ProductionAppError):
    """Raised when configguration is invalid"""
