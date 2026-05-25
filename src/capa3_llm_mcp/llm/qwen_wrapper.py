"""T073 — Wrapper Qwen2.5-7B-Instruct Q4_K_M vía llama-cpp-python.

Modelo: artifacts/llm/qwen2.5-7b-instruct-q4_k_m.gguf  (no en git, ~4.7 GB)
Descarga: huggingface-cli download Qwen/Qwen2.5-7B-Instruct-GGUF \\
              qwen2.5-7b-instruct-q4_k_m.gguf \\
              --local-dir artifacts/llm/

Hardware objetivo: RTX 5070 8 GB VRAM → n_gpu_layers=-1 (offload total).
Temperature: 0.0 en producción (NFR-009 / ADR-0005).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]

_DEFAULT_MODEL = REPO_ROOT / "artifacts" / "llm" / "qwen2.5-7b-instruct-q4_k_m.gguf"
_N_CTX = 4096
_N_GPU_LAYERS = -1  # -1 = offload total a GPU (RTX 5070)


class QwenWrapper:
    """Wrapper llama-cpp-python para Qwen2.5-7B-Instruct Q4_K_M.

    Carga perezosa: el modelo no se lee de disco hasta la primera llamada a
    ``chat()``. Esto permite importar el módulo en entornos sin el .gguf (CI).
    """

    def __init__(self, model_path: Path | None = None) -> None:
        self._model_path: Path = model_path or _DEFAULT_MODEL
        self._llm: Any = None

    # ── disponibilidad ────────────────────────────────────────────────────────

    def is_available(self) -> bool:
        """True si el archivo .gguf existe en disco."""
        return self._model_path.exists()

    # ── carga ─────────────────────────────────────────────────────────────────

    def _load(self) -> None:
        if not self.is_available():
            raise FileNotFoundError(
                f"Modelo no encontrado: {self._model_path}\n"
                "Descarga con: huggingface-cli download Qwen/Qwen2.5-7B-Instruct-GGUF "
                "qwen2.5-7b-instruct-q4_k_m.gguf --local-dir artifacts/llm/"
            )
        try:
            from llama_cpp import Llama  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError(
                "llama-cpp-python no instalado.\n"
                "Instala con soporte CUDA: "
                "CMAKE_ARGS='-DGGML_CUDA=on' pip install llama-cpp-python"
            ) from exc
        self._llm = Llama(
            model_path=str(self._model_path),
            n_ctx=_N_CTX,
            n_gpu_layers=_N_GPU_LAYERS,
            verbose=False,
        )

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
        if self._llm is None:
            self._load()
        result = self._llm.create_chat_completion(  # type: ignore[union-attr]
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return result["choices"][0]["message"]["content"]
