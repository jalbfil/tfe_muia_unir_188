"""T092 — InferenceLogger: persistencia SQLite + JSONL para auditoría.

SQLite: consultas rápidas sobre log_id, incident_id, timestamp, priority.
JSONL:  registro append-only del JSON completo (base de auditoría reproducible).
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # inserta src/

from contracts import InferenceLog  # type: ignore[import]

_DDL = """
CREATE TABLE IF NOT EXISTS inference_logs (
    log_id          TEXT PRIMARY KEY,
    incident_id     TEXT NOT NULL,
    timestamp_start TEXT NOT NULL,
    timestamp_end   TEXT NOT NULL,
    priority        TEXT NOT NULL,
    model_capa2     TEXT NOT NULL,
    model_capa3     TEXT,
    degraded        INTEGER NOT NULL DEFAULT 0,
    input_hash      TEXT NOT NULL,
    json_full       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_incident ON inference_logs(incident_id);
CREATE INDEX IF NOT EXISTS idx_ts ON inference_logs(timestamp_start);
CREATE INDEX IF NOT EXISTS idx_priority ON inference_logs(priority);
"""


class InferenceLogger:
    """Escribe InferenceLog en SQLite (búsqueda) y JSONL (auditoría)."""

    def __init__(self, db_path: Path, jsonl_path: Path) -> None:
        self._db_path = db_path
        self._jsonl_path = jsonl_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    # ── inicialización ────────────────────────────────────────────────────

    def _init_db(self) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.executescript(_DDL)

    # ── escritura ─────────────────────────────────────────────────────────

    def log(self, entry: InferenceLog) -> None:
        """Persiste una entrada de log en SQLite + JSONL."""
        priority = entry.capa2_output.priority_recommended.value
        model_capa2 = entry.model_versions.get("capa2", "")
        model_capa3 = entry.model_versions.get("capa3")
        degraded = int(
            entry.capa3_output is not None
            and "degraded" in (entry.capa3_output.llm_metadata.llm_model or "")
        )
        json_full = entry.model_dump_json()

        # SQLite
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO inference_logs
                    (log_id, incident_id, timestamp_start, timestamp_end,
                     priority, model_capa2, model_capa3, degraded, input_hash, json_full)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.log_id,
                    entry.incident_id,
                    entry.timestamp_start.isoformat(),
                    entry.timestamp_end.isoformat(),
                    priority,
                    model_capa2,
                    model_capa3,
                    degraded,
                    entry.input_hash,
                    json_full,
                ),
            )

        # JSONL append-only
        with self._jsonl_path.open("a", encoding="utf-8") as fh:
            fh.write(json_full + "\n")

    # ── consultas ─────────────────────────────────────────────────────────

    def get_by_log_id(self, log_id: str) -> InferenceLog | None:
        """Recupera un log completo por su ULID."""
        with sqlite3.connect(self._db_path) as conn:
            row = conn.execute(
                "SELECT json_full FROM inference_logs WHERE log_id = ?", (log_id,)
            ).fetchone()
        if row is None:
            return None
        return InferenceLog.model_validate_json(row[0])

    def update_operator_decision(self, log_id: str, updated_entry: InferenceLog) -> None:
        """Actualiza el json_full de una entrada con la decisión del operador."""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "UPDATE inference_logs SET json_full = ? WHERE log_id = ?",
                (updated_entry.model_dump_json(), log_id),
            )
