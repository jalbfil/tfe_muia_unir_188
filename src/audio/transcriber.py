"""Módulo de transcripción de audio para el DSS 112 CyL.

Usa faster-whisper (CTranslate2) para transcripción local sin APIs externas,
cumpliendo el Principio VI (soberanía del dato) del TFE.

Modos de ejecución:
    - GPU (CUDA): automático si hay GPU disponible (RTX 5070 recomendada).
    - CPU: fallback si no hay GPU. Más lento pero funcional.

Modelo por defecto: "small" (balanceo rapidez/precisión en español).
Configurable por WHISPER_MODEL: tiny | base | small | medium | large-v3

Uso básico:
    transcriber = AudioTranscriber()
    if transcriber.is_available():
        text = transcriber.transcribe(audio_bytes)
"""

from __future__ import annotations

import io
import logging
import os
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = os.environ.get("WHISPER_MODEL", "small")
_DEFAULT_LANGUAGE = os.environ.get("WHISPER_LANGUAGE", "es")  # español 112 CyL


class AudioTranscriber:
    """Wrapper de faster-whisper para transcripción offline.

    faster-whisper descarga el modelo la primera vez (~150 MB para small).
    Los modelos se cachean en el directorio de HuggingFace Hub estándar.
    """

    def __init__(
        self,
        model_name: str = _DEFAULT_MODEL,
        language: str = _DEFAULT_LANGUAGE,
    ) -> None:
        self._model_name = model_name
        self._language = language
        self._model = None  # carga lazy

    def is_available(self) -> bool:
        """True si faster-whisper está instalado (no requiere modelo descargado)."""
        try:
            import faster_whisper  # type: ignore[import]  # noqa: F401
            return True
        except ImportError:
            return False

    def _load_model(self) -> object:
        """Carga el modelo con aceleración GPU si está disponible."""
        if self._model is not None:
            return self._model

        from faster_whisper import WhisperModel  # type: ignore[import]

        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
        except ImportError:
            device = "cpu"
            compute_type = "int8"

        logger.info(
            "Cargando Whisper modelo='%s' device='%s' compute='%s'",
            self._model_name, device, compute_type,
        )
        self._model = WhisperModel(
            self._model_name,
            device=device,
            compute_type=compute_type,
        )
        return self._model

    def transcribe(self, audio_bytes: bytes, *, file_ext: str = ".wav") -> str:
        """Transcribe audio bytes a texto en español.

        Args:
            audio_bytes: Contenido binario del archivo de audio
                         (WAV, MP3, MP4, M4A, OGG, WEBM).
            file_ext: Extensión del archivo incluyendo punto (por defecto .wav).

        Returns:
            Texto transcrito. Cadena vacía si el audio no contiene voz.

        Raises:
            RuntimeError: Si faster-whisper no está instalado.
        """
        if not self.is_available():
            raise RuntimeError(
                "faster-whisper no instalado. "
                "Instala con: pip install faster-whisper"
            )

        model = self._load_model()

        # Escribir a fichero temporal (faster-whisper necesita ruta)
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            segments, info = model.transcribe(
                tmp_path,
                language=self._language,
                beam_size=5,
                vad_filter=True,          # filtra silencios (VAD)
                vad_parameters={"min_silence_duration_ms": 300},
            )
            logger.info(
                "Transcripcion: idioma detectado='%s' prob=%.2f",
                info.language, info.language_probability,
            )
            text = " ".join(seg.text.strip() for seg in segments)
            return text.strip()
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def language(self) -> str:
        return self._language
