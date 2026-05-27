# `tfm188-contracts` — Capa de contratos vinculantes

Paquete Pydantic v2 que materializa el **Principio VIII** de la constitución (`Contratos antes que código`).

Cualquier intercambio entre Capa 1 (NLP), Capa 2 (RuleFit) y Capa 3 (LLM/MCP) DEBE pasar por estos modelos. La inferencia se rechaza si la validación falla — sin fallbacks silenciosos.

## Instalación aislada

```bash
pip install -e ./src/contracts
```

(También se instala transitivamente vía el `pyproject.toml` raíz del repositorio.)

## Modelos públicos

| Entidad | Módulo |
|---|---|
| `IncidentInput` (E-01) | [`contracts.incident_input`](contracts/incident_input.py) |
| `IncidentFeatures` (E-02) | [`contracts.incident_features`](contracts/incident_features.py) |
| `PriorityRecommendation` (E-03) | [`contracts.priority_recommendation`](contracts/priority_recommendation.py) |
| `OperatorRecommendation` (E-04) | [`contracts.operator_recommendation`](contracts/operator_recommendation.py) |
| `OperatorDecision` (E-05) | [`contracts.operator_decision`](contracts/operator_decision.py) |
| `OperationalRule` (E-06) | [`contracts.rule`](contracts/rule.py) |
| `WeakLabel` (E-07) | [`contracts.weak_label`](contracts/weak_label.py) |
| `InferenceLog` (E-08) | [`contracts.inference_log`](contracts/inference_log.py) |

## Decisiones arquitectónicas

Ver [`docs/adr/`](docs/adr/).
