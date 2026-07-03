"""T073 - Wrapper LLM local via Ollama.

Runtime: Ollama daemon in http://localhost:11434.
Default model: llama3.1:8b-instruct-q4_K_M, configurable with OLLAMA_MODEL.

This wrapper uses Ollama's native HTTP API directly, so no OpenAI client
dependency is required.
"""

from __future__ import annotations

import json
import logging
import os
from collections.abc import Generator

logger = logging.getLogger(__name__)

_OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
_OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
_DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b-instruct-q4_K_M")
# Cold-start tolerante: cargar un modelo cuantizado de ~5 GB en memoria puede
# superar los 2 s. Un umbral demasiado bajo provoca falsos negativos en
# is_available() y degradacion innecesaria de la Capa 3. Configurable por entorno.
_TIMEOUT_AVAIL = float(os.environ.get("OLLAMA_AVAIL_TIMEOUT", "10.0"))
_TIMEOUT_CHAT = float(os.environ.get("OLLAMA_CHAT_TIMEOUT", "120.0"))


class QwenWrapper:
    """Small Ollama chat wrapper used by Capa 3.

    The historical class name is kept for compatibility with the rest of the
    project, although the default model now points to Llama 3.1 via Ollama.
    """

    def __init__(self, model_name: str = _DEFAULT_MODEL) -> None:
        self._model_name = model_name
        self._resolved_model_name: str | None = None
        logger.info("LLM configurado: %s", self._model_name)

    @property
    def model_name(self) -> str:
        return self._resolved_model_name or self._model_name

    def _resolve_model_name(self) -> str | None:
        """Return the exact local Ollama tag if available."""

        if self._resolved_model_name:
            return self._resolved_model_name

        import httpx  # type: ignore[import]

        response = httpx.get(_OLLAMA_TAGS_URL, timeout=_TIMEOUT_AVAIL)
        if response.status_code != 200:
            return None

        models = [model["name"] for model in response.json().get("models", [])]
        for name in models:
            if name == self._model_name:
                self._resolved_model_name = name
                return name

        for name in models:
            # Accept partial matches because Ollama tags vary by quantization suffix.
            if self._model_name in name or name in self._model_name:
                self._resolved_model_name = name
                return name

        # Fallback si no hay coincidencia exacta o parcial: usar cualquier modelo que contenga 'llama' o 'qwen'
        for name in models:
            if "llama" in name.lower() or "qwen" in name.lower():
                self._resolved_model_name = name
                logger.warning("Modelo '%s' no encontrado. Usando fallback por familia: '%s'", self._model_name, name)
                return name

        # Fallback final: usar el primer modelo disponible en Ollama
        if models:
            self._resolved_model_name = models[0]
            logger.warning("Modelo '%s' no encontrado. Usando primer modelo disponible: '%s'", self._model_name, models[0])
            return models[0]

        return None

    def is_available(self) -> bool:
        """True when Ollama is running and the requested model exists locally."""

        try:
            return self._resolve_model_name() is not None
        except Exception as exc:
            logger.debug("Ollama no disponible: %s", exc)
            return False

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        max_tokens: int = 600,
        temperature: float = 0.0,
        response_format: str | None = None,
    ) -> str:
        """Generate a complete chat response."""

        import httpx  # type: ignore[import]

        model = self._resolve_model_name()
        if model is None:
            raise RuntimeError(f"Modelo Ollama no disponible: {self._model_name}")

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        if response_format:
            payload["format"] = response_format

        response = httpx.post(
            _OLLAMA_CHAT_URL,
            json=payload,
            timeout=_TIMEOUT_CHAT,
        )
        response.raise_for_status()
        return str(response.json().get("message", {}).get("content", "") or "")

    def chat_stream(
        self,
        messages: list[dict[str, str]],
        *,
        max_tokens: int = 600,
        temperature: float = 0.0,
        response_format: str | None = None,
    ) -> Generator[str, None, None]:
        """Yield incremental text chunks from Ollama streaming."""

        import httpx  # type: ignore[import]

        model = self._resolve_model_name()
        if model is None:
            raise RuntimeError(f"Modelo Ollama no disponible: {self._model_name}")

        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        if response_format:
            payload["format"] = response_format

        with httpx.stream(
            "POST",
            _OLLAMA_CHAT_URL,
            json=payload,
            timeout=_TIMEOUT_CHAT,
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                content = chunk.get("message", {}).get("content")
                if content:
                    yield str(content)
