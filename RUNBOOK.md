# RUNBOOK — Sistema de apoyo a la decisión 112 CyL

Guía operativa para arrancar el prototipo en local en **menos de 5 minutos**.
Si algo falla, ve directo a [Troubleshooting](#troubleshooting).

---

## 1 · Pre-requisitos (una sola vez)

| Componente | Versión mínima | Comprobación |
|------------|----------------|--------------|
| Python | 3.11–3.12 | `python --version` |
| [uv](https://docs.astral.sh/uv/) | 0.9+ | `uv --version` |
| [Ollama](https://ollama.com/download) | 0.18+ | `ollama --version` |
| Git | 2.40+ | `git --version` |

### Bootstrap del entorno

```bash
# 1. Clonar e instalar dependencias reproducibles
git clone https://github.com/bripedev-source/tfe_muia_unir_188.git
cd tfe_muia_unir_188
uv sync                    # crea .venv/ desde uv.lock

# 2. Descargar el modelo LLM (~4.7 GB)
ollama pull llama3.1:8b-instruct-q4_K_M
```

> `uv sync` instala desde `uv.lock` (reproducible). Si modificas `pyproject.toml`, ejecuta `uv lock` para regenerar el lock.

> **Alternativas de modelo** — configura `OLLAMA_MODEL=<nombre>` antes de arrancar el backend:
> - `deepseek-r1:7b-q4_K_M` — razonamiento estructurado (ligeramente más lento)
> - `qwen2.5:7b-instruct-q4_K_M` — opción anterior (sigue siendo válida)

---

## 2 · Arranque rápido (3 terminales)

Abre **3 terminales** desde la raíz del repo. Cada uno mantiene un servicio vivo.

### Terminal 1 — LLM local
```bash
ollama serve
```
Verifica: <http://localhost:11434> debe responder `Ollama is running`.

### Terminal 2 — Backend FastAPI
```bash
uv run uvicorn src.backend.api.main:app --reload --port 8000
```
Verifica:
- Salud: `curl http://localhost:8000/health` → `{"status":"ok"}`
- Agent Card: <http://localhost:8000/.well-known/agent.json>
- OpenAPI: <http://localhost:8000/docs>

### Terminal 3 — UI Streamlit
```bash
uv run streamlit run src/ui/app.py
```
Abre automáticamente <http://localhost:8501>.

> **Alternativa VS Code**: `Ctrl+Shift+P → Tasks: Run Task → Up: All` levanta los 3 servicios en paralelo.

---

## 3 · Verificación E2E (2 min)

1. Abre la UI en <http://localhost:8501>.
2. Sidebar debe mostrar **LLM: ✅ online** y **RAG: ✅ disponible** (si está en modo degradado, revisa Troubleshooting).
3. Pestaña **Triage** → escribe:
   > *"Incendio en cocina de bar concurrido en el centro de Burgos, hay humo denso, varias personas atrapadas en la planta superior."*
   - Provincia: `Burgos`, Localidad: `Burgos`.
4. Pulsa **🔍 Analizar incidente**.
5. Debes ver:
   - Banda superior roja con **P1**
   - Tokens del LLM llegando en streaming
   - 3 columnas: Situación / Por qué / Pasos sugeridos
   - Reglas activadas y citas legales visibles

---

## 4 · Tests

```bash
uv run pytest -q                              # toda la suite
uv run pytest tests/test_backend_api.py -v    # sólo API
uv run pytest -m "not slow"                   # rápidos
```

---

## 5 · Apagado limpio

En cada terminal: `Ctrl+C`. Si Ollama queda colgado:
```bash
# Windows
taskkill /F /IM ollama.exe
# Linux/macOS
pkill -f "ollama serve"
```

---

## Troubleshooting

### UI en "modo degradado"
- **Síntoma**: Sidebar muestra `LLM: ⚠️ offline`.
- **Causa**: Ollama no responde en `localhost:11434`.
- **Fix**: arranca el Terminal 1 (`ollama serve`) y espera 5 s. La UI revalida cada 60 s.

### `Port 8000 already in use`
```bash
# Windows
netstat -ano | findstr :8000
taskkill /F /PID <PID>
# Linux/macOS
lsof -ti:8000 | xargs kill -9
```

### `ollama: model not found`
```bash
ollama pull llama3.1:8b-instruct-q4_K_M
ollama list                # confirma que aparece
```

### `uv sync` falla con error de toolchain
```bash
uv python install 3.12      # instala Python gestionado por uv
uv sync --python 3.12
```

### Streamlit no recarga cambios
Pulsa `R` en la propia UI o reinicia el Terminal 3.

### Tests fallan por imports
```bash
uv pip install -e .         # reinstala el paquete en modo editable
```

---

## 6 · Comandos útiles

| Acción | Comando |
|--------|---------|
| Añadir dependencia | `uv add <paquete>` |
| Añadir dev dep | `uv add --dev <paquete>` |
| Regenerar lock | `uv lock` |
| Actualizar deps | `uv lock --upgrade` |
| Ejecutar script | `uv run python scripts/<archivo>.py` |
| Linter + formateador | `uv run ruff check . && uv run ruff format .` |
| Type-check | `uv run mypy src/contracts` |

---

## 7 · Estructura de servicios

```
┌─────────────────┐   HTTP    ┌──────────────────┐  OpenAI API  ┌──────────┐
│ Streamlit (UI)  │ ────────▶ │ FastAPI (API)    │ ───────────▶ │ Ollama   │
│   :8501         │ ◀──SSE─── │   :8000          │ ◀────────── │  :11434  │
└─────────────────┘           └──────────────────┘              └──────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ Pipeline 3 capas │
                              │ Capa 1 → 2 → 3   │
                              └──────────────────┘
```

---

**Última revisión**: 2026-05-27 · Mantiene: equipo TFE MUIA UNIR 188.
