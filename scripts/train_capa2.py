"""T054 - Train Capa 2 RuleFit one-vs-rest on weak labels."""

from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

import joblib  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from imodels import RuleFitClassifier  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.isotonic import IsotonicRegression  # noqa: E402
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support  # noqa: E402
from sklearn.tree import DecisionTreeClassifier, _tree  # noqa: E402

from capa2_rulefit.rulefit import FEATURE_NAMES, RuleFitOvRModel, RuleSetClassifierModel, row_to_vector  # noqa: E402

DEFAULT_CLEAN = (
    PROJECT_ROOT
    / "resources"
    / "dataset"
    / "processed"
    / "emergencias_112_cyl_2008_2022_clean.csv"
)
DEFAULT_SPLIT_DIR = PROJECT_ROOT / "resources" / "dataset" / "splits"
DEFAULT_MODEL_DIR = PROJECT_ROOT / "artifacts" / "models" / "capa2" / "v0.1.0"
DEFAULT_REPORT = PROJECT_ROOT / "artifacts" / "reports" / "rulefit_v0.1.0.json"
DEFAULT_RULES = DEFAULT_MODEL_DIR / "rules.json"
DEFAULT_MODEL = DEFAULT_MODEL_DIR / "rulefit.joblib"
LABELS = ["P1", "P2", "P3", "P4"]


def _rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _load_joined(split_dir: Path, clean_csv: Path, split_name: str) -> pd.DataFrame:
    split = pd.read_csv(split_dir / f"{split_name}.csv")
    clean = pd.read_csv(clean_csv)
    clean = clean.rename(columns={"Identificador": "incident_id"})
    clean["incident_id"] = clean["incident_id"].astype(str)
    split["incident_id"] = split["incident_id"].astype(str)
    joined = split.merge(clean, on="incident_id", how="left", suffixes=("", "_clean"))
    if joined["FechaIncidente"].isna().any():
        missing = int(joined["FechaIncidente"].isna().sum())
        raise RuntimeError(f"{missing} split rows could not be joined with the clean dataset")
    return joined


def _matrix(df: pd.DataFrame) -> np.ndarray:
    rows = df.to_dict(orient="records")
    return np.asarray([row_to_vector(row, FEATURE_NAMES) for row in rows], dtype=float)


def _labels(df: pd.DataFrame) -> np.ndarray:
    return df["final_label"].astype(str).to_numpy()


def _sample_train(df: pd.DataFrame, max_rows: int, random_state: int) -> pd.DataFrame:
    if max_rows <= 0 or len(df) <= max_rows:
        return df
    frac = max_rows / len(df)
    parts = []
    for _, group in df.groupby("final_label", group_keys=False):
        n_rows = max(1, int(round(len(group) * frac)))
        parts.append(group.sample(n_rows, random_state=random_state))
    sampled = pd.concat(parts, ignore_index=True)
    return sampled.sample(frac=1.0, random_state=random_state).reset_index(drop=True)


def _active_rules(estimator: Any, label: str) -> list[dict[str, Any]]:
    rules = estimator._get_rules()
    records: list[dict[str, Any]] = []
    for idx, row in rules.iterrows():
        coef = float(row.get("coef", 0.0))
        if abs(coef) <= 1e-12:
            continue
        records.append(
            {
                "rule_id": f"RF-{label}-{len(records) + 1:03d}",
                "class_label": label,
                "rule": str(row.get("rule", row.get("rule/natural language", ""))),
                "coef": coef,
                "support": float(row.get("support", 0.0)),
                "type": str(row.get("type", "rule")),
            }
        )
    return records


def _train_models(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray,
    y_val: np.ndarray,
    random_state: int,
    alpha: float,
    n_estimators: int,
) -> tuple[RuleFitOvRModel, dict[str, Any]]:
    estimators: dict[str, Any] = {}
    calibrators: dict[str, Any] = {}
    rules_by_class: dict[str, list[dict[str, Any]]] = {}
    for label in LABELS:
        y_binary = (y_train == label).astype(int)
        estimator = RuleFitClassifier(
            n_estimators=n_estimators,
            tree_size=3,
            sample_fract=0.7,
            max_rules=80,
            alpha=alpha,
            cv=False,
            include_linear=True,
            random_state=random_state,
        )
        estimator.fit(x_train, y_binary, feature_names=list(FEATURE_NAMES))
        val_raw = estimator.predict_proba(x_val)[:, 1]
        calibrator = IsotonicRegression(out_of_bounds="clip")
        calibrator.fit(val_raw, (y_val == label).astype(int))
        estimators[label] = estimator
        calibrators[label] = calibrator
        rules_by_class[label] = _active_rules(estimator, label)

    model = RuleFitOvRModel(
        class_labels=LABELS,
        feature_names=list(FEATURE_NAMES),
        estimators=estimators,
        calibrators=calibrators,
        rules_by_class=rules_by_class,
    )
    val_predictions = _predict_labels(model, x_val)
    macro_f1 = f1_score(y_val, val_predictions, labels=LABELS, average="macro")
    active_rule_count = sum(len(rules) for rules in rules_by_class.values())
    summary = {
        "engine": "imodels_rulefit_ovr",
        "alpha": alpha,
        "n_estimators": n_estimators,
        "val_macro_f1": round(float(macro_f1), 6),
        "active_rule_count": active_rule_count,
    }
    return model, summary


def _tree_rule_text(tree: DecisionTreeClassifier, leaf_id: int) -> str:
    tree_ = tree.tree_
    path: list[str] = []

    def visit(node: int, clauses: list[str]) -> bool:
        if node == leaf_id:
            path.extend(clauses)
            return True
        if tree_.feature[node] == _tree.TREE_UNDEFINED:
            return False
        feature = FEATURE_NAMES[tree_.feature[node]]
        threshold = tree_.threshold[node]
        left = f"{feature} <= {threshold:.3f}"
        right = f"{feature} > {threshold:.3f}"
        return visit(tree_.children_left[node], clauses + [left]) or visit(
            tree_.children_right[node],
            clauses + [right],
        )

    visit(0, [])
    return " & ".join(path) if path else "TRUE"


def _fit_lite_model(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray,
    y_val: np.ndarray,
    random_state: int,
) -> tuple[RuleSetClassifierModel, dict[str, Any]]:
    trees: dict[str, DecisionTreeClassifier] = {}
    leaf_values: dict[str, list[int]] = {}
    for label in LABELS:
        y_binary = (y_train == label).astype(int)
        tree = DecisionTreeClassifier(
            max_depth=3,
            min_samples_leaf=30,
            class_weight="balanced",
            random_state=random_state,
        )
        tree.fit(x_train, y_binary)
        trees[label] = tree
        leaf_values[label] = sorted(int(value) for value in np.unique(tree.apply(x_train)))

    seed_model = RuleSetClassifierModel(
        class_labels=LABELS,
        feature_names=list(FEATURE_NAMES),
        trees=trees,
        leaf_values=leaf_values,
        classifier=None,
        calibrators={},
        rules_by_class={},
    )
    x_train_rules = seed_model.transform(x_train)
    x_val_rules = seed_model.transform(x_val)
    classifier = LogisticRegression(
        penalty="l1",
        solver="saga",
        class_weight="balanced",
        max_iter=2000,
        random_state=random_state,
    )
    classifier.fit(x_train_rules, y_train)
    calibrators = {label: None for label in LABELS}

    rules_by_class: dict[str, list[dict[str, Any]]] = {label: [] for label in LABELS}
    feature_offset = len(FEATURE_NAMES)
    coef = classifier.coef_
    for class_idx, class_label in enumerate(classifier.classes_):
        for label in LABELS:
            for leaf_id in leaf_values[label]:
                coef_idx = feature_offset
                for prior_label in LABELS:
                    if prior_label == label:
                        break
                    coef_idx += len(leaf_values[prior_label])
                coef_idx += leaf_values[label].index(leaf_id)
                weight = float(coef[class_idx, coef_idx])
                if abs(weight) <= 1e-8:
                    continue
                rules_by_class[str(class_label)].append(
                    {
                        "rule_id": f"RF-{class_label}-{len(rules_by_class[str(class_label)]) + 1:03d}",
                        "class_label": str(class_label),
                        "rule": _tree_rule_text(trees[label], leaf_id),
                        "coef": weight,
                        "support": float(np.mean(trees[label].apply(x_train) == leaf_id)),
                        "type": "tree_rule",
                    }
                )

    model = RuleSetClassifierModel(
        class_labels=LABELS,
        feature_names=list(FEATURE_NAMES),
        trees=trees,
        leaf_values=leaf_values,
        classifier=classifier,
        calibrators=calibrators,
        rules_by_class=rules_by_class,
    )
    val_predictions = _predict_labels(model, x_val)
    return model, {
        "engine": "sklearn_rulefit_lite",
        "val_macro_f1": round(float(f1_score(y_val, val_predictions, labels=LABELS, average="macro")), 6),
        "active_rule_count": sum(len(rules) for rules in rules_by_class.values()),
    }


def _predict_proba_matrix(model: Any, x: np.ndarray) -> np.ndarray:
    rows = []
    for vector in x:
        row = dict(zip(model.feature_names, vector.tolist()))
        proba = model.predict_proba_from_row(row)
        rows.append([proba[label] for label in LABELS])
    return np.asarray(rows, dtype=float)


def _predict_labels(model: RuleFitOvRModel, x: np.ndarray) -> np.ndarray:
    probs = _predict_proba_matrix(model, x)
    return np.asarray([LABELS[int(np.argmax(row))] for row in probs])


def _evaluate(model: Any, x: np.ndarray, y_true: np.ndarray) -> dict[str, Any]:
    y_pred = _predict_labels(model, x)
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=LABELS,
        zero_division=0,
    )
    cm = confusion_matrix(y_true, y_pred, labels=LABELS)
    per_class = {
        label: {
            "precision": round(float(precision[i]), 6),
            "recall": round(float(recall[i]), 6),
            "f1": round(float(f1[i]), 6),
            "support": int(support[i]),
        }
        for i, label in enumerate(LABELS)
    }
    return {
        "rows": int(len(y_true)),
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 6),
        "macro_f1": round(float(f1_score(y_true, y_pred, labels=LABELS, average="macro")), 6),
        "recall_p1": per_class["P1"]["recall"],
        "per_class": per_class,
        "confusion_matrix": {
            label: {pred: int(cm[i, j]) for j, pred in enumerate(LABELS)}
            for i, label in enumerate(LABELS)
        },
    }


def _mean_inference_ms(model: Any, x: np.ndarray, repeats: int = 5) -> float:
    sample = x[: min(256, len(x))]
    if len(sample) == 0:
        return 0.0
    started = time.perf_counter()
    for _ in range(repeats):
        _predict_labels(model, sample)
    elapsed = time.perf_counter() - started
    return round((elapsed / (repeats * len(sample))) * 1000, 6)


def _write_rules(model: Any, path: Path) -> None:
    all_rules = []
    for label in LABELS:
        all_rules.extend(model.top_rules_for_label(label, limit=30))
    selected = sorted(all_rules, key=lambda rule: abs(float(rule["coef"])), reverse=True)[:30]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clean-csv", type=Path, default=DEFAULT_CLEAN)
    parser.add_argument("--split-dir", type=Path, default=DEFAULT_SPLIT_DIR)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--rules-json", type=Path, default=DEFAULT_RULES)
    parser.add_argument("--report-json", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--alpha", type=float, default=0.01)
    parser.add_argument("--n-estimators", type=int, default=10)
    parser.add_argument("--max-train-rows", type=int, default=3000)
    parser.add_argument(
        "--engine",
        choices=("lite", "imodels"),
        default="lite",
        help="lite is the fast RuleFit-style path; imodels trains imodels.RuleFitClassifier OVR.",
    )
    args = parser.parse_args(argv)

    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=UserWarning)

    started = time.perf_counter()
    train = _load_joined(args.split_dir, args.clean_csv, "train")
    val = _load_joined(args.split_dir, args.clean_csv, "val")
    test = _load_joined(args.split_dir, args.clean_csv, "test")
    train_fit = _sample_train(train, args.max_train_rows, args.random_state)
    x_train, y_train = _matrix(train_fit), _labels(train_fit)
    x_train_full, y_train_full = _matrix(train), _labels(train)
    x_val, y_val = _matrix(val), _labels(val)
    x_test, y_test = _matrix(test), _labels(test)

    if args.engine == "imodels":
        model, selection = _train_models(
            x_train,
            y_train,
            x_val,
            y_val,
            args.random_state,
            args.alpha,
            args.n_estimators,
        )
    else:
        model, selection = _fit_lite_model(x_train, y_train, x_val, y_val, args.random_state)
    training_seconds = round(time.perf_counter() - started, 6)
    args.model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, args.model_path)
    _write_rules(model, args.rules_json)
    active_rule_count = sum(len(rules) for rules in model.rules_by_class.values())
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": "rulefit_one_vs_rest" if args.engine == "imodels" else "rulefit_lite_ruleset",
        "model_version_capa2": model.model_version,
        "feature_names": model.feature_names,
        "class_labels": model.class_labels,
        "selection": selection,
        "fit_rows": int(len(train_fit)),
        "engine": args.engine,
        "training_seconds": training_seconds,
        "model_size_bytes": int(args.model_path.stat().st_size),
        "mean_inference_ms_per_row": _mean_inference_ms(model, x_test),
        "active_rule_count_total": active_rule_count,
        "active_rule_count_exported": min(active_rule_count, 30),
        "artifacts": {
            "model_path": _rel(args.model_path),
            "rules_json": _rel(args.rules_json),
        },
        "splits": {
            "train": _evaluate(model, x_train_full, y_train_full),
            "val": _evaluate(model, x_val, y_val),
            "test": _evaluate(model, x_test, y_test),
        },
        "notes": [
            "imodels.RuleFitClassifier is binary in imodels 2.0.4; P1-P4 uses one-vs-rest.",
            "The lite engine uses shallow tree rules plus a sparse logistic layer as a fast RuleFit-style bridge.",
            "The imodels engine calibrates outputs with isotonic regression on the validation split.",
            "The lite engine stores direct sparse-logistic probabilities to avoid isotonic collapse on rare P4.",
        ],
    }
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        "[OK] RuleFit trained "
        f"val_macro_f1={report['splits']['val']['macro_f1']} "
        f"test_macro_f1={report['splits']['test']['macro_f1']} "
        f"rules={report['active_rule_count_exported']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
