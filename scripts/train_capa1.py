"""Deprecated placeholder for Capa 1 transformer training.

Capa 1 v0.1.0 is intentionally deterministic. This script is kept only to make
that scope explicit and to avoid generating simulated transformer checkpoints or
metrics that could be misread as validated results.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CAPA1_REPORT = REPO_ROOT / "artifacts" / "reports" / "capa1_v0.1.0.json"
E2E_REPORT = REPO_ROOT / "artifacts" / "reports" / "capa1_capa2_e2e_v0.1.0.json"


class RobertaMultitaskClassifier:
    """Compatibility placeholder.

    Transformer training is out of scope for v0.1.0. Do not instantiate this class
    as a model.
    """

    def __init__(self, *_args: object, **_kwargs: object) -> None:
        raise RuntimeError(
            "Capa 1 v0.1.0 is deterministic; transformer training is out of scope."
        )


HAS_TORCH_HF = False


def run_training() -> None:
    """Report the frozen v0.1.0 scope instead of training a transformer."""
    print("Capa 1 v0.1.0 is deterministic. No transformer is trained or validated.")
    print(f"Use the deterministic Capa 1 report: {CAPA1_REPORT}")
    print(f"Use the integrated E2E report: {E2E_REPORT}")


if __name__ == "__main__":
    run_training()
