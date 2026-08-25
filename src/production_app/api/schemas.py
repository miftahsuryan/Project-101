from typing import Literal

from pydantic import BaseModel

from production_app.config import Environment


class HealthResponse(BaseModel):
    status: Literal["ok"]
    environment: Environment
