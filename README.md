# TFE MUIA UNIR 188
**Motor de priorización de incidentes para servicios de emergencias**  
Trabajo Fin de Estudios grupal — Máster Universitario en Inteligencia Artificial (UNIR)  
Director: Dr. Andrés Soto Villaverde

---

## Equipo

| Integrante | Rol principal |
|---|---|
| Juan Carlos Albert Fillol | Coordinación, diseño del motor, marco normativo |
| Brian Mathias Pesci Juliani | Backend, API, integración de IA |
| Ancor González Carballo | Frontend, interfaz de operador |

---

## Arranque rápido

```bash
uv sync                                   # entorno reproducible
ollama pull llama3.1:8b-instruct-q4_K_M   # LLM local (una vez, ~4.7 GB)
pip install faster-whisper                # transcripción de voz (opcional)
```

**Opción A — Gestor interactivo (recomendado):**
```bash
python scripts/services.py   # menú para arrancar/detener/ver logs
```

**Opción B — Manual (3 terminales):**
```bash
ollama serve                                                       # T1
uv run uvicorn src.backend.api.main:app --reload --port 8000       # T2
uv run streamlit run src/ui/app.py                                 # T3
```

Guía completa: [RUNBOOK.md](RUNBOOK.md).

---

## Estructura del repositorio

```
tfe_muia_unir_188/
├── .specify/             # Spec-Driven Development (GitHub Spec Kit)
│   └── memory/
│       ├── constitution.md     # Principios inmutables I–X (v1.0.0)
│       └── amendments.log      # Registro de enmiendas constitucionales
├── specs/                # Feature specs (spec / plan / research / data-model / contracts / tasks)
│   └── 001-priorizacion-112-cyl/
├── src/                  # Código fuente del prototipo
│   ├── contracts/        # Contratos Pydantic v2 (gate Principio VIII)
│   ├── capa1_nlp/        # Extractor NER + V01–V15 (Ancor)
│   ├── capa2_rulefit/    # Motor RuleFit + baseline + ceiling (Juan Carlos)
│   ├── capa3_llm_mcp/    # LLM local + servidor MCP + RAG (Brian)
│   ├── backend/          # FastAPI orquestador
│   └── ui/               # Streamlit UI mínima
├── scripts/              # Pipelines de datos, entrenamiento, evaluación
├── tests/                # Tests de integración cross-capa
├── artifacts/            # Modelos, índices, reportes (ignorado en git)
├── resources/
│   ├── dataset/          # Datos 112 CyL 2008–2022 (raw / processed / audit)
│   └── corpus_normativo/ # Normativa CyL para RAG (T060)
├── latex/                # Memoria del TFM (LaTeX)
│   ├── chapters/         # Capítulos y anexos (.tex)
│   ├── resources/        # Borradores en Markdown
│   ├── figures/          # Imágenes y logos
│   └── build/            # Generado automáticamente (ignorado en git)
├── pyproject.toml        # Configuración Python (ruff, mypy, pytest, coverage)
├── .pre-commit-config.yaml
└── .github/              # CI workflows + plantillas PR/issues + agentes Copilot
```

> **Principios del proyecto**: ver [`.specify/memory/constitution.md`](.specify/memory/constitution.md) — diez principios inmutables que gobiernan todas las decisiones técnicas y narrativas.
> **Feature activa**: ver [`specs/001-priorizacion-112-cyl/README.md`](specs/001-priorizacion-112-cyl/README.md).

---

## Configuración del entorno

### Clonar el repositorio
```bash
git clone https://github.com/jalbfil/tfe_muia_unir_188.git
cd tfe_muia_unir_188
```

### Abrir en VS Code
Usar el workspace configurado para cargar correctamente LaTeX Workshop y los settings del proyecto:
```bash
code tfe_muia_unir_188.code-workspace
```

### LaTeX
Requisitos: [TeX Live](https://tug.org/texlive/) o [MiKTeX](https://miktex.org/) + extensión [LaTeX Workshop](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop).  
Al guardar `latex/main.tex` se compila automáticamente en `latex/build/`.

---

## Flujo de trabajo con Git

```
rama personal (brian/x, ancor/x, juan/x)
        ↓  PR
       dev   ← integración continua
        ↓  merge cuando el hito esté completo
       main  ← versión estable
```

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para la convención de commits y el proceso de PR.

---

## Convención de commits (resumen)

```
feat: nueva funcionalidad     fix: corrección
latex: cambio en la memoria   docs: documentación
chore: mantenimiento          refactor: reestructuración
```
