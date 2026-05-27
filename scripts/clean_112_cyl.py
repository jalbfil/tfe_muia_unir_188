import html
import re
from pathlib import Path

import pandas as pd

# ============================================================
# RUTAS DEL PROYECTO
# ============================================================
# Este script está pensado para ejecutarse desde la raíz del repo:
# C:\Users\juanc\Desktop\UNIR\TFE\tfe_muia_unir_188
#
# Estructura esperada:
# resources/
# └── dataset/
#     ├── raw/
#     │   └── Emergencias2008-2022.csv
#     ├── audit/
#     │   ├── resumen_auditoria_112_cyl.txt
#     │   ├── schema_112_cyl_auditado.csv
#     │   └── mapeo_dataset_motor_112_cyl.csv
#     └── processed/
# ============================================================

PROJECT_ROOT = Path.cwd()

DATASET_DIR = PROJECT_ROOT / "resources" / "dataset"
RAW_DIR = DATASET_DIR / "raw"
AUDIT_DIR = DATASET_DIR / "audit"
OUT_DIR = DATASET_DIR / "processed"

RAW_PATH = RAW_DIR / "Emergencias2008-2022.csv"

OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_CLEAN = OUT_DIR / "emergencias_112_cyl_2008_2022_clean.csv"
OUT_SAMPLE = OUT_DIR / "emergencias_112_cyl_2008_2022_clean_sample.csv"
OUT_REPORT = OUT_DIR / "reporte_limpieza_112_cyl.txt"


def read_csv_robust(path: Path) -> pd.DataFrame:
    """
    Intenta leer el CSV con varias combinaciones habituales en datasets públicos españoles.
    """
    attempts = [
        {"sep": ";", "encoding": "utf-8"},
        {"sep": ";", "encoding": "utf-8-sig"},
        {"sep": ";", "encoding": "latin1"},
        {"sep": ",", "encoding": "utf-8"},
        {"sep": ",", "encoding": "utf-8-sig"},
        {"sep": ",", "encoding": "latin1"},
    ]

    last_error = None

    for kwargs in attempts:
        try:
            df = pd.read_csv(path, **kwargs)
            if df.shape[1] > 1:
                print(f"[OK] CSV leído con {kwargs}")
                return df
        except Exception as exc:
            last_error = exc

    raise RuntimeError(f"No se pudo leer el CSV. Último error: {last_error}")


def clean_html_text(value) -> str:
    """
    Limpia texto con etiquetas HTML y entidades HTML.
    """
    if pd.isna(value):
        return ""

    text = str(value)

    # Decodificar entidades HTML: &nbsp;, &aacute;, etc.
    text = html.unescape(text)

    # Sustituir saltos típicos HTML por espacios.
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"</p\s*>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"</li\s*>", " ", text, flags=re.IGNORECASE)

    # Eliminar etiquetas HTML.
    text = re.sub(r"<[^>]+>", " ", text)

    # Normalizar espacios.
    text = re.sub(r"\s+", " ", text).strip()

    return text


def normalize_text(value) -> str:
    """
    Normaliza texto para reglas simples:
    - minúsculas;
    - sin tildes;
    - sin ñ;
    - sin espacios duplicados.
    """
    text = clean_html_text(value).lower()

    replacements = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ü": "u",
        "ñ": "n",
    }

    for src, dst in replacements.items():
        text = text.replace(src, dst)

    text = re.sub(r"\s+", " ", text).strip()

    return text


def parse_coordinates(value):
    """
    La columna Localidad.1 suele venir como:
    latitud#longitud#codigo

    Ejemplo:
    41.2060230876#-5.46474555991#88
    """
    if pd.isna(value):
        return pd.Series([pd.NA, pd.NA, pd.NA])

    parts = str(value).split("#")

    lat = pd.NA
    lon = pd.NA
    code = pd.NA

    import contextlib
    if len(parts) >= 1:
        with contextlib.suppress(Exception):
            lat = float(parts[0])

    if len(parts) >= 2:
        with contextlib.suppress(Exception):
            lon = float(parts[1])

    if len(parts) >= 3:
        code = parts[2]

    return pd.Series([lat, lon, code])


def contains_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def classify_operational_category(text: str) -> str:
    """
    Clasificación preliminar basada en patrones.

    Esta categoría NO sustituye a la guía de etiquetado ni constituye una verdad oficial.
    Sirve únicamente para mapear el dataset real a una taxonomía operativa preliminar.
    """

    rules = [
        (
            "trafico",
            [
                r"\baccidente\b",
                r"\bcolision\b",
                r"\bcolisión\b",
                r"\bsalida de via\b",
                r"\bsalida de vía\b",
                r"\batropell",
                r"\bmotorista\b",
                r"\bturismo\b",
                r"\bcamion\b",
                r"\bcamión\b",
                r"\bcarretera\b",
                r"\bautovia\b",
                r"\bautovía\b",
                r"\bvehiculo\b",
                r"\bvehículo\b",
            ],
        ),
        (
            "incendio",
            [
                r"\bincendio\b",
                r"\bfuego\b",
                r"\barde\b",
                r"\bllamas\b",
                r"\bhumo\b",
                r"\bforestal\b",
                r"\bvivienda ardiendo\b",
            ],
        ),
        (
            "sanitario",
            [
                r"\bherido\b",
                r"\bherida\b",
                r"\bheridos\b",
                r"\bheridas\b",
                r"\bintoxic",
                r"\bindispuesto\b",
                r"\binconsciente\b",
                r"\bparada cardiorrespiratoria\b",
                r"\buvi movil\b",
                r"\buvi móvil\b",
                r"\bsoporte vital\b",
                r"\bsacyl\b",
            ],
        ),
        (
            "rescate_salvamento",
            [
                r"\batrapad",
                r"\brescate\b",
                r"\bdesaparecid",
                r"\bprecipitad",
                r"\bmontana\b",
                r"\bmontaña\b",
                r"\brio\b",
                r"\brío\b",
                r"\bpozo\b",
                r"\bascensor\b",
                r"\bexcarcel",
            ],
        ),
        (
            "meteorologico_inundacion",
            [
                r"\binundacion\b",
                r"\binundación\b",
                r"\blluvia\b",
                r"\btormenta\b",
                r"\bdesbord",
                r"\bavenida\b",
                r"\briada\b",
                r"\bnieve\b",
                r"\bviento\b",
            ],
        ),
        (
            "seguridad",
            [
                r"\bagresion\b",
                r"\bagresión\b",
                r"\bpelea\b",
                r"\brobo\b",
                r"\bviolencia\b",
                r"\bamenaza\b",
                r"\bpolicia\b",
                r"\bpolicía\b",
            ],
        ),
        (
            "tecnologico_hazmat",
            [
                r"\bquimic",
                r"\bquímic",
                r"\bmercancias peligrosas\b",
                r"\bmercancías peligrosas\b",
                r"\bfuga de gas\b",
                r"\bmonoxido\b",
                r"\bmonóxido\b",
                r"\bexplosion\b",
                r"\bexplosión\b",
                r"\bderrame\b",
            ],
        ),
    ]

    for category, patterns in rules:
        if contains_any(text, patterns):
            return category

    return "otros_no_clasificado"


def check_required_columns(df: pd.DataFrame):
    """
    Comprueba que el CSV contiene las columnas mínimas que hemos auditado.
    """
    required = [
        "Título",
        "DescripcionBlob",
        "FechaIncidente",
        "Localidad",
        "Localidad.1",
        "TipoIncidente",
        "MediosMov",
        "PacientesAten",
        "Identificador",
        "ultimaActualizacion",
        "Enlace al contenido",
    ]

    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(
            "Faltan columnas esperadas en el CSV. "
            f"Columnas ausentes: {missing}. "
            f"Columnas encontradas: {list(df.columns)}"
        )


def main():
    print("==============================================")
    print("LIMPIEZA DATASET 112 CASTILLA Y LEÓN")
    print("==============================================")
    print(f"Directorio actual: {PROJECT_ROOT}")
    print(f"Ruta dataset esperada: {RAW_PATH}")
    print("")

    if not RAW_PATH.exists():
        raise FileNotFoundError(
            "No se encuentra el fichero CSV.\n"
            f"Ruta esperada: {RAW_PATH}\n\n"
            "Comprueba que estás ejecutando el script desde la raíz del repo:\n"
            "C:\\Users\\juanc\\Desktop\\UNIR\\TFE\\tfe_muia_unir_188\n\n"
            "Y que el CSV está en:\n"
            "resources\\dataset\\raw\\Emergencias2008-2022.csv"
        )

    df = read_csv_robust(RAW_PATH)
    check_required_columns(df)

    original_rows = len(df)
    original_cols = list(df.columns)

    # Eliminar columna vacía si existe.
    if "Unnamed: 13" in df.columns:
        df = df.drop(columns=["Unnamed: 13"])

    # Limpieza y conversión de fecha.
    df["FechaIncidente_raw"] = df["FechaIncidente"]
    df["FechaIncidente"] = pd.to_datetime(
        df["FechaIncidente"].astype(str),
        format="%Y%m%d",
        errors="coerce",
    )

    # Filtrar rango válido 2008-2022.
    valid_start = pd.Timestamp("2008-01-01")
    valid_end = pd.Timestamp("2022-12-31")

    df["fecha_valida_2008_2022"] = df["FechaIncidente"].between(
        valid_start,
        valid_end,
    )

    anomalous_dates = df[~df["fecha_valida_2008_2022"]].copy()
    df = df[df["fecha_valida_2008_2022"]].copy()

    # Variables temporales.
    df["anio"] = df["FechaIncidente"].dt.year
    df["mes"] = df["FechaIncidente"].dt.month
    df["dia"] = df["FechaIncidente"].dt.day
    df["dia_semana"] = df["FechaIncidente"].dt.day_name()

    # Limpieza textual.
    df["titulo_limpio"] = df["Título"].apply(clean_html_text)
    df["descripcion_limpia"] = df["DescripcionBlob"].apply(clean_html_text)
    df["medios_mov_limpio"] = df["MediosMov"].apply(clean_html_text)
    df["pacientes_aten_limpio"] = df["PacientesAten"].apply(clean_html_text)

    df["texto_operativo"] = (
        df["titulo_limpio"].fillna("") + " " + df["descripcion_limpia"].fillna("")
    ).str.strip()

    df["texto_operativo_norm"] = df["texto_operativo"].apply(normalize_text)

    # Coordenadas.
    coord_cols = df["Localidad.1"].apply(parse_coordinates)
    coord_cols.columns = ["latitud", "longitud", "codigo_localidad_coord"]
    df = pd.concat([df, coord_cols], axis=1)

    df["tiene_coordenadas"] = df["latitud"].notna() & df["longitud"].notna()

    # Señales operativas extraídas de texto.
    text = df["texto_operativo_norm"]

    df["signal_fallecido"] = text.str.contains(
        r"\bfallecid|\bmuert|\bcadaver|\bcadáver|\bperdio la vida|\bperdió la vida",
        regex=True,
        na=False,
    )

    df["signal_herido_grave"] = text.str.contains(
        r"\bherid[oa] grave|\bgrave|\binconsciente|\bcritico|\bcrítico|\bparada cardiorrespiratoria",
        regex=True,
        na=False,
    )

    df["signal_atrapado"] = text.str.contains(
        r"\batrapad|\bencarcelad|\bno puede salir|\bexcarcelacion|\bexcarcelación",
        regex=True,
        na=False,
    )

    df["signal_intoxicacion"] = text.str.contains(
        r"\bintoxic|\bmonoxido|\bmonóxido|\binhalacion de humo|\binhalación de humo|\bgas",
        regex=True,
        na=False,
    )

    df["signal_varias_llamadas"] = text.str.contains(
        r"\bvarias llamadas|\bvarios avisos|\bnumerosas llamadas|\bse reciben varias",
        regex=True,
        na=False,
    )

    df["signal_incendio"] = text.str.contains(
        r"\bincendio|\bfuego|\bllamas|\bhumo|\barde",
        regex=True,
        na=False,
    )

    df["signal_accidente_trafico"] = text.str.contains(
        r"\baccidente|\bcolision|\bcolisión|\bsalida de via|\bsalida de vía|\batropell|\bmotorista|\bcarretera|\bautovia|\bautovía",
        regex=True,
        na=False,
    )

    df["signal_rescate"] = text.str.contains(
        r"\brescate|\bdesaparecid|\bprecipitad|\batrapad|\bmontana|\bmontaña|\bpozo",
        regex=True,
        na=False,
    )

    df["signal_meteo_inundacion"] = text.str.contains(
        r"\binundacion|\binundación|\blluvia|\btormenta|\bdesbord|\briada|\bavenida|\bnieve|\bviento",
        regex=True,
        na=False,
    )

    # Categoría operativa preliminar.
    df["categoria_operativa_preliminar"] = df["texto_operativo_norm"].apply(
        classify_operational_category
    )

    # Riesgo vital textual preliminar.
    df["riesgo_vital_textual"] = (
        df["signal_fallecido"]
        | df["signal_herido_grave"]
        | df["signal_atrapado"]
        | df["signal_intoxicacion"]
    )

    # Marcar campos que NO deben usarse como entrada principal del motor.
    # MediosMov se considera posterior a la primera decisión y puede introducir fuga de información.
    df["medios_mov_uso_recomendado"] = "validacion_auxiliar_no_input_principal"

    # Ordenar columnas útiles al principio.
    preferred_order = [
        "Identificador",
        "FechaIncidente",
        "anio",
        "mes",
        "dia",
        "dia_semana",
        "Título",
        "titulo_limpio",
        "DescripcionBlob",
        "descripcion_limpia",
        "texto_operativo",
        "texto_operativo_norm",
        "Localidad",
        "Localidad.1",
        "latitud",
        "longitud",
        "codigo_localidad_coord",
        "tiene_coordenadas",
        "TipoIncidente",
        "categoria_operativa_preliminar",
        "riesgo_vital_textual",
        "signal_fallecido",
        "signal_herido_grave",
        "signal_atrapado",
        "signal_intoxicacion",
        "signal_varias_llamadas",
        "signal_incendio",
        "signal_accidente_trafico",
        "signal_rescate",
        "signal_meteo_inundacion",
        "MediosMov",
        "medios_mov_limpio",
        "medios_mov_uso_recomendado",
        "PacientesAten",
        "pacientes_aten_limpio",
        "IncidenteCerrado",
        "Enlace al contenido",
        "ultimaActualizacion",
        "FechaIncidente_raw",
        "fecha_valida_2008_2022",
    ]

    existing_preferred = [c for c in preferred_order if c in df.columns]
    remaining = [c for c in df.columns if c not in existing_preferred]
    df = df[existing_preferred + remaining]

    # Guardar outputs.
    df.to_csv(OUT_CLEAN, index=False, encoding="utf-8-sig")
    df.head(200).to_csv(OUT_SAMPLE, index=False, encoding="utf-8-sig")

    # Reporte.
    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        f.write("REPORTE DE LIMPIEZA DATASET 112 CASTILLA Y LEÓN\n")
        f.write("=" * 60 + "\n\n")

        f.write(f"Directorio de ejecución: {PROJECT_ROOT}\n")
        f.write(f"Archivo origen: {RAW_PATH}\n")
        f.write(f"Archivo limpio generado: {OUT_CLEAN}\n")
        f.write(f"Muestra generada: {OUT_SAMPLE}\n\n")

        f.write(f"Registros originales: {original_rows}\n")
        f.write(f"Registros tras limpieza de fechas: {len(df)}\n")
        f.write(f"Registros eliminados por fecha anómala: {len(anomalous_dates)}\n")
        f.write(f"Columnas originales: {original_cols}\n")
        f.write(f"Columnas finales: {list(df.columns)}\n\n")

        f.write("Fechas anómalas eliminadas:\n")
        if len(anomalous_dates) == 0:
            f.write("No se detectaron fechas anómalas.\n")
        else:
            for _, row in anomalous_dates.iterrows():
                f.write(
                    f"- Identificador={row.get('Identificador')}, "
                    f"FechaIncidente_raw={row.get('FechaIncidente_raw')}, "
                    f"Título={row.get('Título')}\n"
                )

        f.write("\nCobertura de coordenadas:\n")
        f.write(f"- Registros con coordenadas: {int(df['tiene_coordenadas'].sum())}\n")
        f.write(f"- Registros sin coordenadas: {int((~df['tiene_coordenadas']).sum())}\n")
        f.write(
            f"- Porcentaje con coordenadas: "
            f"{round(df['tiene_coordenadas'].mean() * 100, 2)} %\n\n"
        )

        f.write("Distribución de categoría operativa preliminar:\n")
        f.write(df["categoria_operativa_preliminar"].value_counts(dropna=False).to_string())
        f.write("\n\n")

        f.write("Señales operativas extraídas:\n")
        signal_cols = [
            "riesgo_vital_textual",
            "signal_fallecido",
            "signal_herido_grave",
            "signal_atrapado",
            "signal_intoxicacion",
            "signal_varias_llamadas",
            "signal_incendio",
            "signal_accidente_trafico",
            "signal_rescate",
            "signal_meteo_inundacion",
        ]

        for col in signal_cols:
            f.write(f"- {col}: {int(df[col].sum())}\n")

        f.write("\nNota metodológica:\n")
        f.write(
            "El campo MediosMov se conserva para validación auxiliar y análisis de complejidad, "
            "pero no se recomienda emplearlo como entrada principal del motor de primera decisión, "
            "ya que puede reflejar actuaciones posteriores a la valoración inicial y generar fuga de información.\n"
        )

    print("")
    print("[OK] Limpieza completada.")
    print(f"[OK] Dataset limpio: {OUT_CLEAN}")
    print(f"[OK] Muestra: {OUT_SAMPLE}")
    print(f"[OK] Reporte: {OUT_REPORT}")


if __name__ == "__main__":
    main()