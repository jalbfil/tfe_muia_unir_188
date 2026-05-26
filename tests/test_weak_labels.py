from __future__ import annotations

import csv
from pathlib import Path

from scripts.build_weak_labels import build_labels


def _write_fixture(path: Path) -> None:
    rows = [
        {
            "Identificador": "1",
            "FechaIncidente": "2022-01-01",
            "anio": "2022",
            "titulo_limpio": "Fallecido en accidente en Burgos",
            "descripcion_limpia": "Accidente con fallecido y heridas graves",
            "texto_operativo_norm": "accidente fallecido heridas graves (Burgos)",
            "categoria_operativa_preliminar": "trafico",
            "signal_fallecido": "True",
            "signal_herido_grave": "True",
            "signal_atrapado": "False",
            "signal_intoxicacion": "False",
            "signal_varias_llamadas": "True",
            "signal_incendio": "False",
            "signal_accidente_trafico": "True",
            "signal_rescate": "False",
            "signal_meteo_inundacion": "False",
        },
        {
            "Identificador": "2",
            "FechaIncidente": "2021-01-01",
            "anio": "2021",
            "titulo_limpio": "Incendio con atrapados en Leon",
            "descripcion_limpia": "Incendio en vivienda con una persona atrapada",
            "texto_operativo_norm": "incendio vivienda atrapado (Leon)",
            "categoria_operativa_preliminar": "incendio",
            "signal_fallecido": "False",
            "signal_herido_grave": "False",
            "signal_atrapado": "True",
            "signal_intoxicacion": "False",
            "signal_varias_llamadas": "True",
            "signal_incendio": "True",
            "signal_accidente_trafico": "False",
            "signal_rescate": "False",
            "signal_meteo_inundacion": "False",
        },
        {
            "Identificador": "3",
            "FechaIncidente": "2020-01-01",
            "anio": "2020",
            "titulo_limpio": "Aviso informativo en Valladolid",
            "descripcion_limpia": "Incidencia sin heridos",
            "texto_operativo_norm": "aviso informativo sin heridos (Valladolid)",
            "categoria_operativa_preliminar": "otros",
            "signal_fallecido": "False",
            "signal_herido_grave": "False",
            "signal_atrapado": "False",
            "signal_intoxicacion": "False",
            "signal_varias_llamadas": "False",
            "signal_incendio": "False",
            "signal_accidente_trafico": "False",
            "signal_rescate": "False",
            "signal_meteo_inundacion": "False",
        },
    ]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_weak_labels_reach_minimum_agreement(tmp_path: Path) -> None:
    input_csv = tmp_path / "fixture.csv"
    _write_fixture(input_csv)

    rows, report = build_labels(input_csv)

    assert len(rows) == 3
    assert report["krippendorff_alpha_nominal"] >= 0.67
    assert report["alpha_pass"] is True
    assert all(row["final_label"] in {"P1", "P2", "P3", "P4"} for row in rows)


def test_ablation_without_rules_keeps_three_annotators(tmp_path: Path) -> None:
    input_csv = tmp_path / "fixture.csv"
    _write_fixture(input_csv)

    rows, report = build_labels(input_csv, no_rules=True)

    assert len(rows) == 3
    assert len(report["active_annotators"]) == 3
    assert "rules_heuristic" in report["excluded_annotators"]
