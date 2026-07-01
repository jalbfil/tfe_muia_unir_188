"""T046 - Train Capa 1 NLP multilabel classifier on Castile and Leon emergency signals."""

from __future__ import annotations

import json
import time
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multioutput import MultiOutputClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score, precision_score, recall_score

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLEAN_CSV = PROJECT_ROOT / "resources" / "dataset" / "processed" / "emergencias_112_cyl_2008_2022_clean.csv"
SPLIT_DIR = PROJECT_ROOT / "resources" / "dataset" / "splits"
MODEL_DIR = PROJECT_ROOT / "artifacts" / "models" / "capa1" / "v0.1.0"
REPORT_FILE = PROJECT_ROOT / "artifacts" / "reports" / "capa1_v0.1.0.json"

SIGNALS = [
    "signal_fallecido",
    "signal_herido_grave",
    "signal_atrapado",
    "signal_intoxicacion",
    "signal_varias_llamadas",
    "signal_incendio",
    "signal_accidente_trafico",
    "signal_rescate",
    "signal_meteo_inundacion",
    "riesgo_vital_textual",
]


def load_data(split_name: str) -> pd.DataFrame:
    """Loads the split and joins it with the clean dataset to get texts and labels."""
    split = pd.read_csv(SPLIT_DIR / f"{split_name}.csv")
    clean = pd.read_csv(CLEAN_CSV)
    clean = clean.rename(columns={"Identificador": "incident_id"})
    clean["incident_id"] = clean["incident_id"].astype(str)
    split["incident_id"] = split["incident_id"].astype(str)
    joined = split.merge(clean, on="incident_id", how="left")
    
    # Fillna text columns
    joined["texto_operativo"] = joined["texto_operativo"].fillna("")
    
    # Ensure signal columns are boolean/numeric
    for sig in SIGNALS:
        joined[sig] = joined[sig].fillna(False).astype(int)
        
    return joined


def run_training() -> None:
    print("Loading datasets...")
    train_df = load_data("train")
    val_df = load_data("val")
    
    print(f"Loaded {len(train_df)} training rows and {len(val_df)} validation rows.")
    
    X_train = train_df["texto_operativo"].values
    Y_train = train_df[SIGNALS].values
    
    X_val = val_df["texto_operativo"].values
    Y_val = val_df[SIGNALS].values
    
    print("Training TF-IDF + Logistic Regression MultiOutputClassifier...")
    start_time = time.perf_counter()
    
    # Build a simple pipeline
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    classifier = MultiOutputClassifier(LogisticRegression(C=2.0, max_iter=1000, class_weight="balanced"))
    
    X_train_vec = vectorizer.fit_transform(X_train)
    classifier.fit(X_train_vec, Y_train)
    
    train_time = time.perf_counter() - start_time
    print(f"Model trained in {train_time:.2f} seconds.")
    
    # Evaluation
    X_val_vec = vectorizer.transform(X_val)
    Y_val_pred = classifier.predict(X_val_vec)
    
    # Let's compute metrics for each signal
    metrics = {}
    total_f1 = 0.0
    
    print("\n--- Validation Performance per Signal ---")
    for idx, sig in enumerate(SIGNALS):
        precision = precision_score(Y_val[:, idx], Y_val_pred[:, idx], zero_division=0)
        recall = recall_score(Y_val[:, idx], Y_val_pred[:, idx], zero_division=0)
        f1 = f1_score(Y_val[:, idx], Y_val_pred[:, idx], zero_division=0)
        total_f1 += f1
        metrics[sig] = {
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
        }
        print(f"{sig:<25} | Precision: {precision:.4f} | Recall: {recall:.4f} | F1: {f1:.4f}")
        
    mean_f1 = total_f1 / len(SIGNALS)
    print(f"\nMean F1 Score across all signals: {mean_f1:.4f}")
    
    # Create output directory
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    Path(REPORT_FILE.parent).mkdir(parents=True, exist_ok=True)
    
    # Save Pipeline (Vectoriser + Classifier)
    pipeline = {
        "vectorizer": vectorizer,
        "classifier": classifier,
        "signals": SIGNALS,
        "model_version": "0.1.1",
    }
    joblib.dump(pipeline, MODEL_DIR / "classifier.joblib")
    print(f"Saved model pipeline to {MODEL_DIR / 'classifier.joblib'}")
    
    # Save report
    report = {
        "model_name": "TF-IDF + MultiOutput Logistic Regression",
        "model_version": "0.1.1",
        "mean_f1": mean_f1,
        "metrics_per_signal": metrics,
        "training_samples": len(train_df),
        "validation_samples": len(val_df),
        "training_time_seconds": train_time,
    }
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
    print(f"Saved evaluation report to {REPORT_FILE}")


if __name__ == "__main__":
    run_training()
