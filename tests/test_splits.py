from __future__ import annotations

from scripts.build_splits import stratified_split, temporal_split, validate_splits


def _rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    incident_id = 0
    for year in ("2020", "2021", "2022"):
        for province in ("Burgos", "Leon"):
            for label in ("P1", "P2", "P3", "P4"):
                for _ in range(3):
                    incident_id += 1
                    rows.append(
                        {
                            "incident_id": str(incident_id),
                            "anio": year,
                            "provincia_inferida": province,
                            "final_label": label,
                        }
                    )
    return rows


def test_stratified_split_is_disjoint_and_complete() -> None:
    rows = _rows()
    splits = stratified_split(rows, train_ratio=0.70, val_ratio=0.15, seed=42)

    validate_splits(splits)
    assert sum(len(split_rows) for split_rows in splits.values()) == len(rows)
    assert all(splits[name] for name in ("train", "val", "test"))


def test_temporal_split_uses_2021_as_validation_and_2022_as_test() -> None:
    splits = temporal_split(_rows())

    validate_splits(splits)
    assert {row["anio"] for row in splits["train"]} == {"2020"}
    assert {row["anio"] for row in splits["val"]} == {"2021"}
    assert {row["anio"] for row in splits["test"]} == {"2022"}
