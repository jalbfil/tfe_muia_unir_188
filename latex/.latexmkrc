# latexmkrc — configuración para compilar con -outdir=build
# Copia el .bib al directorio build/ para que BibTeX pueda encontrarlo

$bibtex_use = 2;

# Copiar .bib al directorio de salida antes de cada compilación
use File::Copy;
copy("bibliografia.bib", "build/bibliografia.bib") if -d "build";
