"""Parser inteligente de transcripciones de emergencias 112 CyL.

Extrae título, descripción, categoría, localidad y provincia desde el texto
libre del transcript. Usa Ollama si está disponible; si no, heurísticas locales.

Uso:
    parser = TranscriptParser()
    fields = parser.parse("Hay un choque en la N-122 kilómetro 150, hay un herido grave")
    # fields = {"titulo": "...", "descripcion": "...", "categoria": ..., ...}
"""

from __future__ import annotations

import json
import logging
import re

logger = logging.getLogger(__name__)

# ── Mapas de categorías por palabras clave (valores exactos de CategoriaPreliminar) ─
# El orden importa: la primera categoría que matchea gana en la heurística.
_CATEGORIA_KEYWORDS: dict[str, list[str]] = {
    "INCENDIO_FORESTAL": [
        "incendio forestal", "fuego forestal", "monte", "bosque", "vegetación",
        "pasto", "rastrojo", "forestal", "matorral",
    ],
    "QUIMICO_NRBQ": [
        "químico", "gas", "fuga", "tóxico", "cisterna", "vertido", "radiactivo",
        "nrbq", "mercancías peligrosas", "olor químico", "gas licuado",
    ],
    "INCENDIO_URBANO": [
        "incendio", "fuego", "llamas", "humo", "ardiendo", "quema", "arde",
        "vivienda ardiendo",
    ],
    "ACCIDENTE_TRAFICO": [
        "choque", "colisión", "accidente", "tráfico", "coche", "carro", "vehículo",
        "moto", "camión", "carretera", "autovía", "autopista", "km", "kilómetro",
        "atropello", "volcado", "volcar",
    ],
    "SANITARIO": [
        "herido", "lesionado", "inconsciente", "desmayo", "infarto", "parada",
        "ambulancia", "médico", "dolor pecho", "respiración", "caída", "enfermo",
    ],
    "RESCATE": [
        "atrapado", "atrapar", "rescate", "derrumbe", "desprendimiento", "hundimiento",
        "pozo", "barranco", "montaña", "perdido", "ahogado",
    ],
    "METEOROLOGIA": [
        "inundación", "inundado", "granizo", "tormenta", "nieve", "hielo", "viento",
        "temporal", "rambla", "riada",
    ],
    "INCIDENCIA_VIA": [
        "árbol caído", "arbol caido", "obstáculo", "calzada", "señalización",
        "socavón", "arcén", "baden",
    ],
    "SEGURIDAD_CIUDADANA": [
        "pelea", "robo", "agresión", "altercado", "amenaza", "violencia",
    ],
    "SUMINISTROS": [
        "corte de luz", "apagón", "suministro", "agua potable", "telefonía",
    ],
    "OTROS": [],
}

# Provincias de Castilla y León
_PROVINCIAS_CYL: dict[str, list[str]] = {
    "AVILA": ["ávila", "avila"],
    "BURGOS": ["burgos"],
    "LEON": ["león", "leon"],
    "PALENCIA": ["palencia"],
    "SALAMANCA": ["salamanca"],
    "SEGOVIA": ["segovia"],
    "SORIA": ["soria"],
    "VALLADOLID": ["valladolid"],
    "ZAMORA": ["zamora"],
}

_OLLAMA_URL = "http://localhost:11434/api/chat"
_OLLAMA_TIMEOUT = 15.0

_EXTRACT_PROMPT = """\
Eres un asistente del servicio de emergencias 112 de Castilla y León.
Recibes una transcripción automática (Whisper) de una llamada que puede contener
errores fonéticos: nombres de municipios o provincias mal escritos, términos
médicos o técnicos confundidos, palabras pegadas o partidas, etc.

Tu tarea:
1. CORRIGE los errores de transcripción, en especial los topónimos de Castilla y
   León (p. ej. "cegovia" → "Segovia", "ballesteros" → nombre real) y los términos
   de emergencias (p. ej. "oríodos" → "heridos"). NO añadas, inventes ni supongas
   información que no esté en el texto: conserva el sentido literal de la llamada.
2. Extrae la información y devuelve SOLO un objeto JSON con estas claves exactas:

{
  "titulo": "título breve y corregido del incidente (máximo 10 palabras)",
  "descripcion": "el texto completo ya CORREGIDO, sin errores de transcripción",
  "categoria": "una de: ACCIDENTE_TRAFICO | INCENDIO_FORESTAL | INCENDIO_URBANO | INCIDENCIA_VIA | METEOROLOGIA | QUIMICO_NRBQ | RESCATE | SANITARIO | SEGURIDAD_CIUDADANA | SUMINISTROS | OTROS",
  "localidad": "nombre del municipio o localidad corregido si se menciona, o cadena vacía",
  "provincia": "una de: AVILA | BURGOS | LEON | PALENCIA | SALAMANCA | SEGOVIA | SORIA | VALLADOLID | ZAMORA, o cadena vacía"
}

Texto transcrito (puede contener errores):
\"\"\"
{texto}
\"\"\"

Responde SOLO con el JSON. No incluyas explicaciones."""


class TranscriptParser:
    """Extrae campos del formulario 112 desde texto transcrito."""

    def parse(self, texto: str) -> dict:
        """Devuelve dict con: titulo, descripcion, categoria, localidad, provincia."""
        if not texto.strip():
            return self._empty()

        # 1. Intentar con Ollama si está disponible
        try:
            result = self._parse_llm(texto)
            if result:
                logger.info("Transcript parseado con LLM")
                return result
        except Exception as exc:
            logger.debug("LLM no disponible, usando heurísticas: %s", exc)

        # 2. Fallback heurístico
        return self._parse_heuristic(texto)

    def _parse_llm(self, texto: str) -> dict | None:
        """Usa Ollama para extracción estructurada."""
        import httpx  # type: ignore[import]

        # .replace en lugar de .format: el prompt contiene llaves {} del ejemplo
        # JSON que .format() interpretaría como campos (KeyError).
        prompt = _EXTRACT_PROMPT.replace("{texto}", texto[:2000])
        resp = httpx.post(
            _OLLAMA_URL,
            json={
                "model": "llama3.1:8b-instruct-q4_K_M",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {"temperature": 0.0, "num_predict": 800},
            },
            timeout=_OLLAMA_TIMEOUT,
        )
        resp.raise_for_status()
        content = resp.json().get("message", {}).get("content", "")
        parsed = self._extract_json(content)
        if parsed:
            return self._normalise(parsed, texto)
        return None

    def _parse_heuristic(self, texto: str) -> dict:
        """Heurísticas rápidas sin LLM."""
        texto_lower = texto.lower()

        # Título: primera oración / primeras 10 palabras
        first_sentence = re.split(r"[.!?\n]", texto.strip())[0].strip()
        words = first_sentence.split()
        titulo = " ".join(words[:10]).capitalize()
        if len(titulo) < 5:
            titulo = " ".join(texto.split()[:10]).capitalize()

        # Categoría por palabras clave (primera que matchea gana)
        categoria = "OTROS"
        for cat, keywords in _CATEGORIA_KEYWORDS.items():
            if any(kw in texto_lower for kw in keywords):
                categoria = cat
                break

        # Provincia
        provincia = ""
        for prov, aliases in _PROVINCIAS_CYL.items():
            if any(alias in texto_lower for alias in aliases):
                provincia = prov
                break

        # Localidad: buscar patrón "en [Lugar]", "de [Lugar]", "carretera [NXX]"
        localidad = ""
        loc_match = re.search(
            r"\ben\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\s\-]{2,30})(?:\s*,|\s+[a-z]|\s*$)",
            texto,
        )
        if loc_match:
            localidad = loc_match.group(1).strip()

        return {
            "titulo": titulo[:100],
            "descripcion": texto,
            "categoria": categoria,
            "localidad": localidad[:80],
            "provincia": provincia,
        }

    @staticmethod
    def _extract_json(raw: str) -> dict | None:
        start = raw.find("{")
        if start == -1:
            return None
        depth = 0
        for idx in range(start, len(raw)):
            if raw[idx] == "{":
                depth += 1
            elif raw[idx] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(raw[start : idx + 1])
                    except json.JSONDecodeError:
                        return None
        return None

    def _normalise(self, data: dict, texto_original: str) -> dict:
        """Valida y normaliza los campos extraídos por el LLM."""
        from contracts.enums import CategoriaPreliminar, ProvinciaCyL  # type: ignore[import]

        valid_cats = {c.value for c in CategoriaPreliminar}
        cat_raw = str(data.get("categoria", "OTROS")).upper()
        categoria = cat_raw if cat_raw in valid_cats else "OTROS"

        valid_provs = {p.value for p in ProvinciaCyL}
        prov_raw = str(data.get("provincia", "")).upper()
        provincia = prov_raw if prov_raw in valid_provs else ""

        titulo = str(data.get("titulo", "")).strip()[:100]
        if not titulo:
            titulo = " ".join(texto_original.split()[:10]).capitalize()

        # Descripción corregida por el LLM (errores de transcripción). Si el LLM no
        # devuelve descripción, se cae al texto original sin corregir.
        descripcion = str(data.get("descripcion", "")).strip()[:5000] or texto_original

        return {
            "titulo": titulo,
            "descripcion": descripcion,
            "categoria": categoria,
            "localidad": str(data.get("localidad", "")).strip()[:80],
            "provincia": provincia,
        }

    @staticmethod
    def _empty() -> dict:
        return {
            "titulo": "",
            "descripcion": "",
            "categoria": "OTROS",
            "localidad": "",
            "provincia": "",
        }
