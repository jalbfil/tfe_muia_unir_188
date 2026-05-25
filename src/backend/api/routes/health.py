"""GET /healthz y GET /version."""
from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()

_API_VERSION = "0.1.0"
_CONTRACTS_VERSION = "0.1.0"


class HealthResponse(BaseModel):
    status: str
    version: str
    degraded: bool


class VersionResponse(BaseModel):
    api: str
    contracts: str


@router.get("/healthz", response_model=HealthResponse)
def healthz(request: Request) -> HealthResponse:
    llm = getattr(request.app.state, "llm", None)
    return HealthResponse(
        status="ok",
        version=_API_VERSION,
        degraded=(llm is None),
    )


@router.get("/version", response_model=VersionResponse)
def version() -> VersionResponse:
    return VersionResponse(api=_API_VERSION, contracts=_CONTRACTS_VERSION)
