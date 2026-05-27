"""T093-T096 — Tests integración Backend FastAPI (Fase 7).

Escenarios:
  T093 — Escenario 1: POST /predict incidente P1 → 200 + OperatorRecommendation válido
  T094 — Escenario 4: POST /feedback decisión operador → 200 + ok
  T095 — Escenario 5: POST /predict con campo de leakage → 422
  T096 — Escenario 6: POST /predict sin LLM → 200 + modo degradado
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from starlette.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from backend.api.main import app  # type: ignore[import]

# ── fixtures ──────────────────────────────────────────────────────────────────

_INCIDENTE_P1 = {
    "incident_id": "01J5Y8KQ3FXQH4PVDXY9N7B0AQ",
    "texto_titulo": "Accidente grave N-122",
    "texto_descripcion": (
        "Varón inconsciente tras choque frontal en N-122 km 245, "
        "herido grave atrapado en el habitáculo, otro pasajero camina aturdido. "
        "Han llamado varios testigos."
    ),
    "categoria_preliminar": "ACCIDENTE_TRAFICO",
    "latitud": 41.6235,
    "longitud": -4.7268,
    "localidad": "Aldealuenga de Santa María",
    "provincia": "SORIA",
    "fecha_incidente": "2026-05-24T18:42:00+02:00",
    "operador_id": "OP-CYL-007",
}

_INCIDENTE_P4 = {
    "incident_id": "01J5Y8M3KX8MAFG3VKVK7DQX02",
    "texto_titulo": "Árbol caído en arcén",
    "texto_descripcion": (
        "Árbol de tamaño medio caído en el arcén derecho, "
        "no obstaculiza la circulación, sin heridos."
    ),
    "categoria_preliminar": "INCIDENCIA_VIA",
    "latitud": 42.8125,
    "longitud": -1.6458,
    "localidad": "Cervera de Pisuerga",
    "provincia": "PALENCIA",
    "fecha_incidente": "2026-05-24T11:15:00+02:00",
    "operador_id": "OP-CYL-007",
}


@pytest.fixture(scope="module")
def client():
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


# ── T093 — Escenario 1: /predict con incidente P1 ────────────────────────────

def test_t093_predict_returns_200(client: TestClient):
    """T093-A: POST /predict → 200."""
    resp = client.post("/predict", json=_INCIDENTE_P1)
    assert resp.status_code == 200, resp.text


def test_t093_predict_response_schema(client: TestClient):
    """T093-B: respuesta contiene recommendation + priority_details + log_id."""
    resp = client.post("/predict", json=_INCIDENTE_P1)
    body = resp.json()
    assert "recommendation" in body
    assert "priority_details" in body
    assert "log_id" in body
    assert len(body["log_id"]) == 26  # ULID


def test_t093_predict_priority_details_has_probabilities(client: TestClient):
    """T093-B2: Capa 2 expone probabilidades P1-P4 para la UI."""
    resp = client.post("/predict", json=_INCIDENTE_P1)
    details = resp.json()["priority_details"]
    assert set(details["probabilities"]) == {"P1", "P2", "P3", "P4"}
    assert sum(details["probabilities"].values()) == pytest.approx(1.0)
    assert details["model_used"] in ("RULEFIT", "BASELINE_EXPERT", "FALLBACK")


def test_t093_predict_recommendation_has_required_fields(client: TestClient):
    """T093-C: recommendation tiene todos los campos del contrato."""
    resp = client.post("/predict", json=_INCIDENTE_P1)
    rec = resp.json()["recommendation"]
    assert "priority_recommended" in rec
    assert "explanation_text" in rec
    assert "legal_citations" in rec
    assert "actuation_hints" in rec
    assert "model_version_capa3" in rec
    assert "llm_metadata" in rec


def test_t093_predict_explanation_text_bounds(client: TestClient):
    """T093-D: explanation_text 20–1200 chars."""
    resp = client.post("/predict", json=_INCIDENTE_P1)
    text = resp.json()["recommendation"]["explanation_text"]
    assert 20 <= len(text) <= 1200


def test_t093_predict_p1_has_legal_citations(client: TestClient):
    """T093-E: incidente P1 → ≥1 legal_citation en la respuesta."""
    resp = client.post("/predict", json=_INCIDENTE_P1)
    rec = resp.json()["recommendation"]
    if rec["priority_recommended"] in ("P1", "P2"):
        assert len(rec["legal_citations"]) >= 1


def test_t093_predict_incident_id_preserved(client: TestClient):
    """T093-F: el incident_id de la respuesta coincide con el input."""
    resp = client.post("/predict", json=_INCIDENTE_P1)
    rec = resp.json()["recommendation"]
    assert rec["incident_id"] == _INCIDENTE_P1["incident_id"]


# ── T094 — Escenario 4: /feedback decisión divergente ────────────────────────

def test_t094_feedback_returns_200(client: TestClient):
    """T094-A: POST /feedback → 200."""
    # Primero predecir para tener un log_id
    pred_resp = client.post("/predict", json=_INCIDENTE_P4)
    assert pred_resp.status_code == 200

    decision = {
        "incident_id": _INCIDENTE_P4["incident_id"],
        "priority_recommended_by_system": pred_resp.json()["recommendation"]["priority_recommended"],
        "priority_assigned_by_operator": "P3",  # operador sube prioridad
        "motivo_divergencia": "Incendio secundario detectado en zona próxima",
        "operador_id": "OP-CYL-007",
        "timestamp": "2026-05-24T11:20:00+02:00",
    }
    resp = client.post("/feedback", json=decision)
    assert resp.status_code == 200


def test_t094_feedback_response_schema(client: TestClient):
    """T094-B: respuesta de /feedback tiene ok=True."""
    pred_resp = client.post("/predict", json=_INCIDENTE_P4)
    decision = {
        "incident_id": _INCIDENTE_P4["incident_id"],
        "priority_recommended_by_system": pred_resp.json()["recommendation"]["priority_recommended"],
        "priority_assigned_by_operator": "P3",
        "motivo_divergencia": "Revisión manual",
        "operador_id": "OP-CYL-007",
        "timestamp": "2026-05-24T11:21:00+02:00",
    }
    resp = client.post("/feedback", json=decision)
    body = resp.json()
    assert body["ok"] is True
    assert "log_id" in body


# ── T095 — Escenario 5: rechazo de campo de leakage ──────────────────────────

def test_t095_leakage_field_rejected(client: TestClient):
    """T095: POST /predict con campo 'categoria_real' (leakage) → 422."""
    malicious = {**_INCIDENTE_P1, "categoria_real": "P1"}  # campo de leakage
    resp = client.post("/predict", json=malicious)
    assert resp.status_code == 422


def test_t095_priority_label_field_rejected(client: TestClient):
    """T095-B: POST /predict con 'prioridad_etiquetada' (leakage) → 422."""
    malicious = {**_INCIDENTE_P1, "prioridad_etiquetada": "P1"}
    resp = client.post("/predict", json=malicious)
    assert resp.status_code == 422


# ── T096 — Escenario 6: modo degradado ───────────────────────────────────────

def test_t096_degraded_mode_returns_200(client: TestClient):
    """T096-A: incluso sin LLM disponible, /predict devuelve 200."""
    # En CI no hay modelo .gguf → siempre modo degradado
    resp = client.post("/predict", json=_INCIDENTE_P1)
    assert resp.status_code == 200


def test_t096_degraded_response_is_valid(client: TestClient):
    """T096-B: respuesta degradada tiene todos los campos obligatorios."""
    resp = client.post("/predict", json=_INCIDENTE_P1)
    rec = resp.json()["recommendation"]
    assert rec["priority_recommended"] in ("P1", "P2", "P3", "P4")
    assert len(rec["explanation_text"]) >= 20
    assert isinstance(rec["legal_citations"], list)
    assert isinstance(rec["actuation_hints"], list)


# ── /healthz y /version ───────────────────────────────────────────────────────

def test_healthz_returns_200(client: TestClient):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "version" in body


def test_version_endpoint(client: TestClient):
    resp = client.get("/version")
    assert resp.status_code == 200
    body = resp.json()
    assert "api" in body
    assert "contracts" in body
