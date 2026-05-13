# TFE — Sistema inteligente de apoyo a la decisión para puestos de mando de emergencias

**Máster Universitario en Inteligencia Artificial — UNIR**  
Autores: Juan Carlos Albert Fillol · Brian Mathias Pesci Juliani · Ancor González Carballo  
Director: Dr. Andrés Soto Villaverde

---

## Requisitos

| Herramienta | Versión mínima | Notas |
|---|---|---|
| MiKTeX | 25.x | Windows; instala paquetes on-demand |
| latexmk | 4.80+ | Incluido en MiKTeX |
| Perl | 5.x | Necesario para latexmk |
| pandoc | 3.x | Solo para generar `.docx` |
| Python + PyMuPDF | 3.x / 1.27+ | Solo si hay que regenerar `logo_unir.png` |

> En Linux/Mac sustituir MiKTeX por TeX Live.

---

## Configuración con VS Code (recomendado)

El proyecto incluye una carpeta `.vscode/` con toda la configuración necesaria. Al abrir la carpeta en VS Code:

1. VS Code sugerirá instalar las extensiones recomendadas — aceptar.
2. La extensión **LaTeX Workshop** compilará automáticamente al guardar (`Ctrl+S`), generando `build/main.pdf`.
3. El PDF se abre en el visor integrado con SyncTeX (clic en el PDF → salta al `.tex`).
4. Para generar el DOCX: `Terminal → Run Task → Generar DOCX (pandoc)`.
5. Para limpiar auxiliares: `Terminal → Run Task → Limpiar auxiliares (latexmk -C)`.

> La carpeta `build/` queda oculta en el explorador de VS Code (está en `files.exclude`), pero sigue existiendo en disco y en git está ignorada.

---

## Estructura del repositorio

```
main.tex               ← documento raíz (portada, resumen, abstract, \input de capítulos)
plantilla.tex          ← referencia original UNIR (no editar)
estilo_unir-1.sty      ← estilos y portada UNIR (no editar salvo causa mayor)
bibliografia.bib       ← todas las referencias BibTeX (formato APA 7ª ed. — apacite)
apa.csl                ← CSL de APA para pandoc/docx
.latexmkrc             ← configuración de latexmk (copia .bib a build/ automáticamente)
.gitignore             ← ignora build/**

chapters/
  chap0.tex            ← Organización grupal
  chap1.tex            ← Introducción
  chap2.tex            ← Estado del arte
  chap3.tex            ← Marco normativo
  chap4.tex            ← Objetivos
  chap5.tex            ← Requisitos
  chap6.tex            ← Diseño
  chap7.tex            ← Dataset
  chap8.tex            ← Prototipo
  chap9.tex            ← Evaluación
  chap10.tex           ← Conclusiones
  anexo_a.tex … anexo_f.tex

figures/
  logo_unir.png        ← logo UNIR (PNG, no subir el .pdf original al repo)

build/                 ← generado automáticamente, ignorado por git
.vscode/               ← configuración del proyecto para VS Code (versionar)
resources/             ← borradores, rúbrica, indicaciones (no se compila)
```

---

## Compilar el PDF (línea de comandos)

Si no usas VS Code, o quieres compilar desde terminal:

```bash
latexmk -pdf -outdir=build -halt-on-error main.tex
```

El PDF se genera en `build/main.pdf`.

Para limpiar los auxiliares y recompilar desde cero:

```bash
latexmk -C -outdir=build main.tex
latexmk -pdf -outdir=build -halt-on-error main.tex
```

---

## Generar el DOCX (entrega Word)

```bash
pandoc main.tex -o main.docx \
  --bibliography=bibliografia.bib \
  --citeproc \
  --resource-path=chapters:figures:. \
  -M lang=es-ES \
  --csl=apa.csl
```

El archivo se genera como `main.docx` en la raíz. No está versionado en git.

---

## Añadir referencias bibliográficas

Edita `bibliografia.bib` siguiendo el formato BibTeX. Los tipos más usados en el proyecto:

```bibtex
@misc{ClaveCorta,
  author = {Apellido, Nombre},
  title  = {Título del documento},
  year   = {2023},
  url    = {https://...},
  note   = {Consultado el 1 de enero de 2024}
}
```

Cita en el texto con `\cite{ClaveCorta}` o `\citep{ClaveCorta}`.  
El estilo bibliográfico es **APA 7ª edición** (`apacite`).

---

## Flujo de trabajo en equipo

1. Cada autor trabaja en su(s) capítulo(s) en `chapters/`.  
2. Nunca editar `main.tex` para contenido — solo para incluir nuevos capítulos con `\input{}`.  
3. Antes de hacer `git push`, compilar el PDF y asegurarse de que no hay errores.  
4. Los archivos de `build/` **no se versionen** (`.gitignore`).  
5. El `main.docx` tampoco se versiona; se genera bajo demanda.

---

## Regenerar el logo PNG (solo si es necesario)

Si el archivo `figures/logo_unir.png` se pierde, regenerarlo desde `logo_unir.pdf`:

```bash
python -c "
import fitz
doc = fitz.open('logo_unir.pdf')
pix = doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))
pix.save('figures/logo_unir.png')
print('OK:', pix.width, 'x', pix.height)
"
```

Requiere `pip install pymupdf`.
