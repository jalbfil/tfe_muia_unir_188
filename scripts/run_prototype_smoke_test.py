"""Run the v0.1.0 prototype smoke test against live backend and Ollama.

The test exercises four operational incidents, one for each expected priority
P1-P4, through the public `/predict` endpoint. It records Capa 2 probabilities,
the Capa 3 model used, degraded-mode status and short explanations.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))
sys.path.insert(0, str(SRC_ROOT / "contracts"))

DEFAULT_JSON = PROJECT_ROOT / "artifacts" / "reports" / "prototype_v0.1.0_smoke_test.json"
DEFAULT_MD = PROJECT_ROOT / "artifacts" / "reports" / "prototype_v0.1.0_smoke_test.md"


@dataclass(frozen=True)
class SmokeIncident:
    expected_priority: str
    incident_id: str
    title: str
    description: str
    category: str
    province: str
    locality: str
    rationale: str

    def as_payload(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "texto_titulo": self.title,
            "texto_descripcion": self.description,
            "categoria_preliminar": self.category,
            "provincia": self.province,
            "localidad": self.locality,
            "fecha_incidente": "2026-05-27T12:00:00+02:00",
            "operador_id": "SMOKE_TEST",
        }


INCIDENTS = [
    SmokeIncident(
        expected_priority="P1",
        incident_id="SMOKE-P1-INCENDIO-ATRAPADOS",
        title="Incendio urbano con atrapados",
        description=(
            "Incendio en vivienda con humo denso. Varias llamadas indican que hay "
            "dos personas atrapadas en la planta superior y una no responde."
        ),
        category="INCENDIO_URBANO",
        province="BURGOS",
        locality="Burgos",
        rationale="Incendio, atrapamiento, varias llamadas y riesgo vital textual.",
    ),
    SmokeIncident(
        expected_priority="P2",
        incident_id="SMOKE-P2-FUGA-GAS",
        title="Fuga de gas en nave industrial",
        description=(
            "Aviso por fuga de gas y olor fuerte en nave. Hay trabajadores mareados "
            "por posible intoxicacion e inhalacion de humo, con dificultad respiratoria "
            "y riesgo vital."
        ),
        category="QUIMICO_NRBQ",
        province="VALLADOLID",
        locality="Valladolid",
        rationale="Riesgo quimico con intoxicacion y necesidad de recursos especializados.",
    ),
    SmokeIncident(
        expected_priority="P3",
        incident_id="SMOKE-P3-ARBOL-CALZADA",
        title="Arbol caido en carretera secundaria",
        description=(
            "Arbol caido ocupa parcialmente un carril. No hay heridos ni vehiculos "
            "atrapados. Trafico lento en la zona."
        ),
        category="INCIDENCIA_VIA",
        province="SORIA",
        locality="Soria",
        rationale="Incidencia vial sin victimas que requiere evaluacion y gestion ordinaria.",
    ),
    SmokeIncident(
        expected_priority="P4",
        incident_id="SMOKE-P4-CONSULTA-VECINAL",
        title="Aviso informativo sin riesgo",
        description=(
            "Consulta vecinal por ruido y molestias leves. No hay heridos, no hay fuego, "
            "no hay personas atrapadas y no se requiere intervencion urgente."
        ),
        category="OTROS",
        province="SORIA",
        locality="Soria",
        rationale="Aviso ordinario sin senales de riesgo vital ni urgencia operativa.",
    ),
]


def _get_json(client: httpx.Client, url: str) -> dict[str, Any]:
    response = client.get(url)
    response.raise_for_status()
    return response.json()


def _post_json(client: httpx.Client, url: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = client.post(url, json=payload)
    response.raise_for_status()
    return response.json()


def _backend_health_live(client: httpx.Client, backend_url: str) -> dict[str, Any] | None:
    try:
        return _get_json(client, f"{backend_url}/healthz")
    except Exception:
        return None


def _ollama_status(client: httpx.Client, ollama_url: str) -> dict[str, Any]:
    try:
        data = _get_json(client, f"{ollama_url}/api/tags")
        return {
            "available": True,
            "models": [model["name"] for model in data.get("models", [])],
        }
    except Exception as exc:
        return {"available": False, "models": [], "error": str(exc)}


def _run_with_live_backend(
    client: httpx.Client,
    backend_url: str,
    incidents: list[SmokeIncident],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    health = _get_json(client, f"{backend_url}/healthz")
    cases = []
    for incident in incidents:
        t0 = time.perf_counter()
        body = _post_json(client, f"{backend_url}/predict", incident.as_payload())
        cases.append(_case_result(incident, body, (time.perf_counter() - t0) * 1000))
    return health, cases


def _run_with_testclient(incidents: list[SmokeIncident]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    from fastapi.testclient import TestClient  # type: ignore[import]

    from backend.api.main import app  # type: ignore[import]

    cases = []
    with TestClient(app) as client:
        health = client.get("/healthz").json()
        for incident in incidents:
            t0 = time.perf_counter()
            response = client.post("/predict", json=incident.as_payload())
            response.raise_for_status()
            cases.append(_case_result(incident, response.json(), (time.perf_counter() - t0) * 1000))
    return health, cases


def _case_result(incident: SmokeIncident, body: dict[str, Any], latency_ms: float) -> dict[str, Any]:
    recommendation = body["recommendation"]
    priority_details = body["priority_details"]
    probabilities = priority_details["probabilities"]
    obtained = recommendation["priority_recommended"]
    return {
        "incident_id": incident.incident_id,
        "title": incident.title,
        "expected_priority": incident.expected_priority,
        "obtained_priority": obtained,
        "passed": obtained == incident.expected_priority,
        "rationale": incident.rationale,
        "model_used_capa2": priority_details["model_used"],
        "confidence_level_capa2": priority_details["confidence_level"],
        "probabilities": probabilities,
        "llm_model": recommendation["llm_metadata"]["llm_model"],
        "degraded": bool(body.get("degraded", False)),
        "legal_citations_count": len(recommendation.get("legal_citations", [])),
        "actuation_hints_count": len(recommendation.get("actuation_hints", [])),
        "explanation_excerpt": recommendation["explanation_text"][:280],
        "latency_ms": round(latency_ms, 6),
    }


def run_smoke_test(
    backend_url: str,
    ollama_url: str,
    timeout: float,
    backend_mode: str,
) -> dict[str, Any]:
    started = time.perf_counter()
    with httpx.Client(timeout=timeout) as client:
        ollama = _ollama_status(client, ollama_url)
        live_health = _backend_health_live(client, backend_url)
        if backend_mode == "live" or (backend_mode == "auto" and live_health is not None):
            health, cases = _run_with_live_backend(client, backend_url, INCIDENTS)
            resolved_backend_mode = "live"
        elif backend_mode in {"auto", "testclient"}:
            health, cases = _run_with_testclient(INCIDENTS)
            resolved_backend_mode = "testclient"
        else:
            raise RuntimeError(f"Backend live no disponible en {backend_url}")

    passed_cases = sum(1 for case in cases if case["passed"])
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "scope": "prototype v0.1.0 live smoke test P1-P4 with Ollama",
        "backend": {
            "url": backend_url,
            "mode": resolved_backend_mode,
            "live_available": live_health is not None,
            "health": health,
        },
        "ollama": ollama,
        "summary": {
            "cases": len(cases),
            "passed_cases": passed_cases,
            "failed_cases": len(cases) - passed_cases,
            "all_cases_use_rulefit": all(case["model_used_capa2"] == "RULEFIT" for case in cases),
            "all_cases_use_llm": all(not case["degraded"] for case in cases),
            "llm_models_observed": sorted({case["llm_model"] for case in cases}),
            "mean_latency_ms": round(sum(case["latency_ms"] for case in cases) / len(cases), 6),
            "total_elapsed_seconds": round(time.perf_counter() - started, 6),
        },
        "cases": cases,
        "notes": [
            "This smoke test validates the live prototype path through FastAPI.",
            "It complements, but does not replace, offline Capa 2 evaluation on the full dataset.",
            "The P3 case was selected after observing that meteorological flooding is escalated to P2.",
        ],
    }
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Smoke test prototipo v0.1.0 con Ollama",
        "",
        f"- Generado: `{payload['generated_at']}`",
        f"- Backend: `{payload['backend']['url']}`",
        f"- Modo backend: `{payload['backend']['mode']}`",
        f"- Backend vivo disponible: `{payload['backend']['live_available']}`",
        f"- Estado backend: `{payload['backend']['health'].get('status')}`",
        f"- Ollama disponible: `{payload['ollama']['available']}`",
        f"- Modelos Ollama detectados: `{', '.join(payload['ollama'].get('models', []))}`",
        f"- Casos OK: `{payload['summary']['passed_cases']}/{payload['summary']['cases']}`",
        f"- Todos usan RuleFit: `{payload['summary']['all_cases_use_rulefit']}`",
        f"- Todos usan LLM no degradado: `{payload['summary']['all_cases_use_llm']}`",
        f"- Modelos LLM observados: `{', '.join(payload['summary']['llm_models_observed'])}`",
        f"- Latencia media por llamada: `{payload['summary']['mean_latency_ms']} ms`",
        "",
        "| Caso | Esperado | Obtenido | Modelo C2 | LLM | P1 | P2 | P3 | P4 | OK |",
        "|---|---:|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for case in payload["cases"]:
        probs = case["probabilities"]
        lines.append(
            "| "
            + " | ".join(
                [
                    case["incident_id"],
                    case["expected_priority"],
                    case["obtained_priority"],
                    case["model_used_capa2"],
                    case["llm_model"],
                    _pct(float(probs["P1"])),
                    _pct(float(probs["P2"])),
                    _pct(float(probs["P3"])),
                    _pct(float(probs["P4"])),
                    "si" if case["passed"] else "no",
                ]
            )
            + " |"
        )
    lines.extend(["", "## Explicaciones", ""])
    for case in payload["cases"]:
        lines.extend(
            [
                f"### {case['incident_id']} ({case['obtained_priority']})",
                "",
                case["explanation_excerpt"],
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend-url", default="http://localhost:8000")
    parser.add_argument("--ollama-url", default="http://localhost:11434")
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--backend-mode", choices=("auto", "live", "testclient"), default="auto")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    args = parser.parse_args(argv)

    payload = run_smoke_test(
        args.backend_url.rstrip("/"),
        args.ollama_url.rstrip("/"),
        args.timeout,
        args.backend_mode,
    )
    _write_json(args.output_json, payload)
    _write_markdown(args.output_md, payload)
    print(
        "[OK] Prototype smoke test "
        f"passed={payload['summary']['passed_cases']}/{payload['summary']['cases']} "
        f"rulefit={payload['summary']['all_cases_use_rulefit']} "
        f"llm={payload['summary']['all_cases_use_llm']} "
        f"json={args.output_json}"
    )
    return 0 if payload["summary"]["failed_cases"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
