"""T073 — Wrapper LLM local vía Ollama (OpenAI-compatible API).

Runtime: Ollama daemon en localhost:11434.
Modelo por defecto: llama3.1:8b-instruct-q4_K_M (~4.7 GB VRAM).
  Alternativas probadas: deepseek-r1:7b-q4_K_M, qwen2.5:7b-instruct-q4_K_M.
  Configurable vía variable de entorno: OLLAMA_MODEL=<nombre>.

Hardware: RTX 5070 8 GB VRAM — Ollama gestiona el offload CUDA automáticamente.
Temperature: 0.0 en producción (NFR-009 / ADR-0005).

Interfaz idéntica al wrapper llama-cpp-python anterior: pipeline y tests
no requieren cambios. La migración a llama-cpp-python directo es posible
en v0.2.0 sin cambiar el contrato.
"""
from __future__ import annotations

import logging
import os
from collections.abc import Generator
from typing import Any

logger = logging.getLogger(__name__)

_OLLAMA_BASE_URL = "http://localhost:11434/v1"
_OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
# Modelo configurable por entorno; cambia con: OLLAMA_MODEL=deepseek-r1:7b-q4_K_M
# Opciones evaluadas (mayo 2026, RTX 5070 8 GB VRAM):
#   llama3.1:8b-instruct-q4_K_M   → primera opción (español + instrucciones)
#   deepseek-r1:7b-q4_K_M          → segunda opción (razonamiento estructurado)
#   qwen2.5:7b-instruct-q4_K_M     → opción anterior (sigue siendo válida)
_DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b-instruct-q4_K_M")
_TIMEOUT_AVAIL = 2.0    # segundos para el healthcheck de disponibilidad
_TIMEOUT_CHAT = 120.0   # segundos para generación (8B Q4 con GPU)


class QwenWrapper:
    """Wrapper para Qwen2.5-7B-Instruct Q4_K_M vía Ollama.

    Carga perezosa: el cliente OpenAI no se inicializa hasta la primera
    llamada a ``chat()``. Esto permite importar el módulo aunque Ollama
    no esté activo (modo degradado en CI/tests sin GPU).
    """

    def __init__(self, model_name: str = _DEFAULT_MODEL) -> None:
        self._model_name = model_name
        self._client: Any = None
        logger.info("LLM configurado: %s", self._model_name)

    # ── disponibilidad ────────────────────────────────────────────────────────

    def is_available(self) -> bool:
        """True si el daemon Ollama está activo y el modelo está descargado."""
        try:
            import httpx  # type: ignore[import]

            r = httpx.get(_OLLAMA_TAGS_URL, timeout=_TIMEOUT_AVAIL)
            if r.status_code != 200:
                return False
            models = [m["name"] for m in r.json().get("models", [])]
            # Aceptar coincidencia parcial: "llama3.1:8b" cubre "llama3.1:8b-instruct-q4_K_M"
            return any(self._model_name in n or n in self._model_name for n in models)
        except Exception as exc:
            logger.debug("Ollama no disponible: %s", exc)
            return False

    # ── cliente (perezoso) ────────────────────────────────────────────────────

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                from openai import OpenAI  # type: ignore[import]
            except ImportError as exc:
                raise ImportError(
                    "openai no instalado. Instala con: pip install openai"
                ) from exc
            self._client = OpenAI(
                base_url=_OLLAMA_BASE_URL,
                api_key="ollama",  # Ollama ignora este valor; requerido por el cliente OpenAI
                timeout=_TIMEOUT_CHAT,
            )
        return self._client

    # ── inferencia ─────────────────────────────────────────────────────────────

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        max_tokens: int = 600,
        temperature: float = 0.0,
    ) -> str:
        """Genera respuesta dado un historial de mensajes (chat format).

        Args:
            messages:     Lista de {"role": "system"|"user"|"assistant", "content": str}.
            max_tokens:   Límite de tokens en la respuesta.
            temperature:  0.0 en producción (NFR-009).

        Returns:
            Texto generado por el modelo.
        """
        client = self._get_client()
        response = client.chat.completions.create(
            model=self._model_name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

    def chat_stream(
        self,
        messages: list[dict[str, str]],
        *,
        max_tokens: int = 600,
        temperature: float = 0.0,
    ) -> Generator[str, None, None]:
        """Genera tokens incrementales vía Ollama streaming.

        Yields:
            Fragmentos de texto según los produce el modelo (token a token).
        """
        client = self._get_client()
        stream = client.chat.completions.create(
            model=self._model_name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
