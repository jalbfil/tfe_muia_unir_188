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

## Estructura del repositorio

```
tfe_muia_unir_188/
├── latex/          # Memoria del TFM (LaTeX)
│   ├── chapters/   # Capítulos y anexos (.tex)
│   ├── resources/  # Borradores en Markdown
│   ├── figures/    # Imágenes y logos
│   └── build/      # Generado automáticamente (ignorado en git)
├── backend/        # Prototipo backend (por inicializar)
├── frontend/       # Prototipo frontend (por inicializar)
├── resources/      # Documentación normativa y de referencia
└── .github/        # Plantillas de PR e issues
```

---

## Configuración del entorno

### Clonar el repositorio
```bash
git clone https://github.com/bripedev-source/tfe_muia_unir_188.git
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
