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
    if llm is None:
        try:
            from capa3_llm_mcp.llm.qwen_wrapper import QwenWrapper
            wrapper = QwenWrapper()
            if wrapper.is_available():
                request.app.state.llm = wrapper
                llm = wrapper
        except Exception:
            pass
    return HealthResponse(
        status="ok",
        version=_API_VERSION,
        degraded=(llm is None),
    )


@router.get("/version", response_model=VersionResponse)
def version() -> VersionResponse:
    return VersionResponse(api=_API_VERSION, contracts=_CONTRACTS_VERSION)
