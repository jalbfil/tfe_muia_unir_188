"""T113 - Independent LLM judge for Capa 3 explanation fidelity.

This judge is complementary to the deterministic offline judge in
``scripts/evaluate_explanation_fidelity.py``. It targets any OpenAI-compatible
chat endpoint, so a local runtime (Ollama at ``/v1``) and an external provider
share the same code path; only ``base_url``, ``api_key`` and ``model`` change.

Configuration (env vars; CLI flags may override model/provider in the script):

- ``FIDELITY_JUDGE_PROVIDER``  -> ``ollama`` (default) or ``openai``
- ``FIDELITY_JUDGE_MODEL``     -> judge model name
- ``FIDELITY_JUDGE_BASE_URL``  -> OpenAI-compatible base URL
- ``FIDELITY_JUDGE_API_KEY``   -> API key (never logged nor persisted)

The judge scores six dimensions in ``[0, 1]``. The aggregation weights are applied
in Python (not by the LLM) to stay comparable with the deterministic rubric:
priority_alignment, rule_traceability, signal_coverage, legal_traceability each
weigh 2.0; no_contradiction and confidence_disclaimer weigh 1.0 (total 10).
"""

from __future__ import annotations

import json
import os
from typing import Any

_DIMENSIONS = (
    "priority_alignment",
    "rule_traceability",
    "signal_coverage",
    "legal_traceability",
    "no_contradiction",
    "confidence_disclaimer",
)
_WEIGHTS = {
    "priority_alignment": 2.0,
    "rule_traceability": 2.0,
    "signal_coverage": 2.0,
    "legal_traceability": 2.0,
    "no_contradiction": 1.0,
    "confidence_disclaimer": 1.0,
}

_DEFAULTS = {
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "model": "llama3.1:8b-instruct-q4_K_M",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "api_key": "",
        "model": "gpt-4o-mini",
    },
}

_SYSTEM_PROMPT = (
    "Eres un evaluador independiente de fidelidad de explicaciones en un sistema "
    "de apoyo a la decisión para emergencias 112. La prioridad P1-P4 ya la decide "
    "un motor interpretable (Capa 2); la explicación solo debe ser fiel a esa "
    "decisión y a su evidencia, sin inventar. Evalúa seis dimensiones, cada una en "
    "el rango [0,1]. Devuelve ÚNICAMENTE un objeto JSON con estas claves exactas: "
    "priority_alignment, rule_traceability, signal_coverage, legal_traceability, "
    "no_contradiction, confidence_disclaimer. No incluyas texto fuera del JSON."
)


class LLMJudgeError(RuntimeError):
    """Raised when the judge cannot run (no endpoint, missing key, etc.)."""


class LLMJudge:
    """Independent fidelity judge over an OpenAI-compatible chat endpoint."""

    def __init__(
        self,
        *,
        provider: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        temperature: float = 0.0,
        timeout: float = 60.0,
        max_retries: int = 2,
    ) -> None:
        self.provider = (provider or os.environ.get("FIDELITY_JUDGE_PROVIDER", "ollama")).lower()
        defaults = _DEFAULTS.get(self.provider, _DEFAULTS["ollama"])
        self.base_url = (
            base_url or os.environ.get("FIDELITY_JUDGE_BASE_URL") or defaults["base_url"]
        ).rstrip("/")
        self.model = model or os.environ.get("FIDELITY_JUDGE_MODEL") or defaults["model"]
        self._api_key = os.environ.get("FIDELITY_JUDGE_API_KEY") or defaults["api_key"]
        self.temperature = temperature
        self.timeout = timeout
        self.max_retries = max(1, max_retries)

    @property
    def public_config(self) -> dict[str, Any]:
        """Config safe to persist (no credentials)."""

        host = self.base_url.split("//", 1)[-1].split("/", 1)[0]
        return {
            "provider": self.provider,
            "model": self.model,
            "base_url_host": host,
            "temperature": self.temperature,
        }

    def is_available(self) -> bool:
        """True when the endpoint responds and a key is present when required."""

        if self.provider == "openai" and not self._api_key:
            return False
        try:
            import httpx  # type: ignore[import]

            response = httpx.get(
                f"{self.base_url}/models",
                headers=self._headers(),
                timeout=min(self.timeout, 5.0),
            )
            return response.status_code == 200
        except Exception:
            return False

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    def _build_user_prompt(self, case_context: dict[str, Any], explanation_text: str) -> str:
        return (
            "Decisión de Capa 2 (no la cambies):\n"
            f"- prioridad_recomendada: {case_context.get('priority_recommended')}\n"
            f"- probabilidades: {case_context.get('probabilities')}\n"
            f"- reglas_resumen: {case_context.get('rules_summary')}\n"
            f"- señales_esperadas: {case_context.get('expected_signals')}\n"
            f"- citas_legales_presentes: {case_context.get('legal_citations_count')}\n"
            f"- requiere_revisión_humana: {case_context.get('requires_human_attention')}\n\n"
            "Explicación generada a evaluar:\n"
            f"\"\"\"\n{explanation_text}\n\"\"\"\n\n"
            "Puntúa cada dimensión en [0,1]:\n"
            "- priority_alignment: menciona y respeta la prioridad de Capa 2.\n"
            "- rule_traceability: se apoya en reglas/evidencias reales.\n"
            "- signal_coverage: cubre las señales esperadas.\n"
            "- legal_traceability: incluye base legal cuando la prioridad es P1/P2.\n"
            "- no_contradiction: no sugiere otra prioridad incompatible.\n"
            "- confidence_disclaimer: comunica cautela o revisión humana.\n"
            "Responde SOLO con el JSON de seis claves."
        )

    def _chat(self, user_prompt: str) -> str:
        import httpx  # type: ignore[import]

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.temperature,
            "stream": False,
        }
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers=self._headers(),
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return str(data["choices"][0]["message"]["content"] or "")

    @staticmethod
    def _extract_json(raw: str) -> dict[str, Any] | None:
        start = raw.find("{")
        if start == -1:
            return None
        depth = 0
        for idx in range(start, len(raw)):
            char = raw[idx]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(raw[start : idx + 1])
                    except json.JSONDecodeError:
                        return None
        return None

    def score(self, case_context: dict[str, Any], explanation_text: str) -> dict[str, Any]:
        """Return judged dimensions, aggregated fidelity and pass flag.

        On parsing failure the case is flagged (``parse_error=True``) instead of
        raising, so a single bad case does not abort a full run.
        """

        user_prompt = self._build_user_prompt(case_context, explanation_text)
        raw = ""
        parsed: dict[str, Any] | None = None
        for _ in range(self.max_retries):
            raw = self._chat(user_prompt)
            parsed = self._extract_json(raw)
            if parsed is not None:
                break
            user_prompt += "\n\nRecuerda: responde EXCLUSIVAMENTE con el JSON válido."

        if parsed is None:
            return {
                "fidelity_score": 0.0,
                "passed": False,
                "parse_error": True,
                "raw_judge_json": raw[:2000],
                **{dimension: 0.0 for dimension in _DIMENSIONS},
            }

        dimensions: dict[str, float] = {}
        parse_warning = False
        for dimension in _DIMENSIONS:
            value = parsed.get(dimension)
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                numeric = 0.0
                parse_warning = True
            dimensions[dimension] = max(0.0, min(1.0, numeric))

        weighted = sum(_WEIGHTS[name] * dimensions[name] for name in _DIMENSIONS)
        fidelity_score = round(weighted / sum(_WEIGHTS.values()), 6)
        passed = (
            fidelity_score >= 0.80
            and dimensions["priority_alignment"] >= 0.5
            and dimensions["legal_traceability"] >= 0.5
            and dimensions["no_contradiction"] >= 0.5
        )
        return {
            "fidelity_score": fidelity_score,
            "passed": passed,
            "parse_error": False,
            "parse_warning": parse_warning,
            "raw_judge_json": json.dumps(parsed, ensure_ascii=False)[:2000],
            **{name: round(dimensions[name], 6) for name in _DIMENSIONS},
        }
