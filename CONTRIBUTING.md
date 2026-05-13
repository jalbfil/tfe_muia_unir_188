# Guía de contribución

## Ramas

| Rama | Propósito |
|---|---|
| `main` | Versión estable. Solo recibe merges desde `dev`. |
| `dev` | Integración continua. Aquí se mergean las ramas personales. |
| `brian/<nombre>` | Trabajo de Brian (backend, API, IA) |
| `ancor/<nombre>` | Trabajo de Ancor (frontend, UI) |
| `juan/<nombre>` | Trabajo de Juan (diseño del motor, latex, coordinación) |

**Flujo:**
```
rama personal → PR a dev → merge a main cuando el hito esté completo
```

## Convención de commits

```
<tipo>: <descripción en imperativo, minúsculas>
```

| Tipo | Cuándo usarlo |
|---|---|
| `feat` | Nueva funcionalidad o contenido nuevo |
| `fix` | Corrección de un error o problema |
| `docs` | Cambios en documentación (sin afectar código) |
| `latex` | Cambios en la memoria (archivos `.tex`, `.bib`) |
| `chore` | Tareas de mantenimiento, configuración, dependencias |
| `refactor` | Reestructuración sin cambio de comportamiento |
| `style` | Formato, espacios, ortografía (sin cambio de lógica) |

**Ejemplos:**
```
feat: implementar endpoint POST /incidents
fix: corregir cálculo de score en caso de variable nula
latex: redactar sección 6.3 reglas duras
chore: actualizar .gitignore con patrones de entorno virtual
```

## Pull Requests

1. Crea tu rama desde `dev` actualizado:
   ```bash
   git checkout dev && git pull
   git checkout -b brian/nombre-tarea
   ```
2. Trabaja en tu rama y haz commits descriptivos.
3. Abre un PR hacia `dev` usando la plantilla disponible.
4. Cualquier miembro del equipo puede revisar y mergear a `dev`.
5. Los merges a `main` los coordina Brian como responsable del repo.
