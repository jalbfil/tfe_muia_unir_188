"""T019 — Exporta JSON Schema de cada modelo público a `src/contracts/docs/schemas/`.

Uso:
    python scripts/export_schemas.py            # regenera y sobrescribe
    python scripts/export_schemas.py --check    # falla si difiere (modo CI)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pydantic import BaseModel

from contracts import (
    IncidentFeatures,
    IncidentInput,
    InferenceLog,
    OperationalRule,
    OperatorDecision,
    OperatorRecommendation,
    PriorityRecommendation,
    WeakLabel,
    __version__,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = REPO_ROOT / "src" / "contracts" / "docs" / "schemas"

PUBLIC_MODELS: list[type[BaseModel]] = [
    IncidentInput,
    IncidentFeatures,
    PriorityRecommendation,
    OperatorRecommendation,
    OperatorDecision,
    OperationalRule,
    WeakLabel,
    InferenceLog,
]


def dump_schema(model: type[BaseModel]) -> str:
    schema = model.model_json_schema(mode="serialization")
    schema["$contractsVersion"] = __version__
    return json.dumps(schema, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_all(target_dir: Path) -> dict[str, str]:
    target_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}
    for model in PUBLIC_MODELS:
        content = dump_schema(model)
        fname = f"{model.__name__}.schema.json"
        (target_dir / fname).write_text(content, encoding="utf-8")
        written[fname] = content
    return written


def check_all(target_dir: Path) -> list[str]:
    diffs: list[str] = []
    for model in PUBLIC_MODELS:
        fname = f"{model.__name__}.schema.json"
        path = target_dir / fname
        if not path.exists():
            diffs.append(f"FALTA: {fname}")
            continue
        on_disk = path.read_text(encoding="utf-8")
        regenerated = dump_schema(model)
        if on_disk != regenerated:
            diffs.append(f"DIFIERE: {fname}")
    return diffs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Modo CI: no escribir, fallar si difiere.")
    args = parser.parse_args()

    if args.check:
        diffs = check_all(SCHEMAS_DIR)
        if diffs:
            print("Schemas divergentes — regenera con `python scripts/export_schemas.py`:", file=sys.stderr)
            for d in diffs:
                print(f"  - {d}", file=sys.stderr)
            return 1
        print(f"OK: {len(PUBLIC_MODELS)} schemas coinciden con disco.")
        return 0

    written = write_all(SCHEMAS_DIR)
    print(f"Escritos {len(written)} schemas en {SCHEMAS_DIR.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
