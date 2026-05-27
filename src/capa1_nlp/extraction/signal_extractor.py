"""Extractor determinista de señales léxicas basado en expresiones regulares."""

from __future__ import annotations

import re
from typing import Any

from contracts import BoolWithConfidence

_NEGATION_WINDOW = 42
_NEGATION_PATTERN = re.compile(
    r"(?:\bno\s+(?:hay|consta|constan|presenta|presentan)\b|\bsin\b|\bni\b|\bning[uú]n\b|\bninguna\b)",
    re.IGNORECASE,
)


class SignalExtractor:
    """Clase encargada de analizar texto libre y extraer 10 señales léxicas obligatorias.
    
    Cada señal se devuelve como BoolWithConfidence con un valor (True/False) y
    una confianza asociada (1.0 por defecto al ser reglas deterministas).
    """

    def __init__(self) -> None:
        # Expresiones regulares optimizadas para emergencias de Castilla y León
        self.patterns = {
            "signal_fallecido": re.compile(
                r"\b(muert[oa]s?|fallecid[oa]s?|cad[aá]ver(es)?|difunt[oa]s?|[oó]bitos?|finad[oa]s?|muerte|decesos?|pcr|parada\s+cardio|fallece(n)?)\b",
                re.IGNORECASE,
            ),
            "signal_herido_grave": re.compile(
                r"\b(grave(s)?|cr[ií]tic[oa]s?|inconsciente?s?|hemorragia\s+masiva|amputaci[oó]n(es)?|fractura\s+abierta|infarto|dolor\s+pecho|ahogamiento|asfixia|quemadura\s+grave|coma|no\s+respira|inconsciencia)\b",
                re.IGNORECASE,
            ),
            "signal_atrapado": re.compile(
                r"\b(atrapad[oa]s?|excarcelar|excarcelaci[oó]n|no\s+puede\s+salir|prensad[oa]s?|aplastad[oa]s?|encerrad[oa]s?|atrapamiento(s)?)\b",
                re.IGNORECASE,
            ),
            "signal_intoxicacion": re.compile(
                r"\b(intoxicaci[oó]n|intoxicad[oa]s?|gases?|humos?|co|mon[oó]xido|qu[ií]mic[oa]s?|olor\s+fuerte|vertidos?|fuga\s+gas|inhalaci[oó]n\s+humo|pesticidas?|venenos?)\b",
                re.IGNORECASE,
            ),
            "signal_varias_llamadas": re.compile(
                r"\b(varias\s+llamadas|m[uú]ltiples\s+avisos|muchas\s+llamadas|segundo\s+aviso|reiteradas\s+llamadas|reiterados\s+avisos)\b",
                re.IGNORECASE,
            ),
            "signal_incendio": re.compile(
                r"\b(incendios?|fuegos?|quemas?|deflagraci[oó]n(es)?|llamas?|forestal(es)?|conatos?|arde(n)?|ardiendo|quemando|chispas?|explosiones?)\b",
                re.IGNORECASE,
            ),
            "signal_accidente_trafico": re.compile(
                r"\b(accidentes?|coches?|colisi[oó]n(es)?|choques?|atropellos?|vuelcos?|cami[oó]n(es)?|motos?|veh[ií]culos?|calzada|carreteras?|autov[ií]as?)\b",
                re.IGNORECASE,
            ),
            "signal_rescate": re.compile(
                r"\b(rescates?|rescatar|auxilios?|socorros?|evacuaci[oó]n(es)?|b[uú]squedas?|atrapado\s+monta[ñn]a|atrapado\s+r[ií]o|helic[oó]pteros?|salvamentos?)\b",
                re.IGNORECASE,
            ),
            "signal_meteo_inundacion": re.compile(
                r"\b(inundaci[oó]n(es)?|inundad[oa]s?|riadas?|desbordamientos?|agua\s+acumulada|tormentas?|granizos?|vientos?\s+fuerte(s)?|temporales?|lluvias?\s+intensa(s)?)\b",
                re.IGNORECASE,
            ),
            "riesgo_vital_textual": re.compile(
                r"\b(riesgo\s+vital|peligro\s+muerte|se\s+muere|parada\s+respiratoria|no\s+responde|asfixi[aá]ndose|ahog[aá]ndose|c[oó]digo\s+rojo|cr[ií]tico|vida\s+peligro)\b",
                re.IGNORECASE,
            ),
        }

    def _has_non_negated_match(self, regex: re.Pattern[str], text: str) -> bool:
        """Return True when a pattern match is not locally negated."""

        for match in regex.finditer(text):
            prefix = text[max(0, match.start() - _NEGATION_WINDOW) : match.start()]
            if not _NEGATION_PATTERN.search(prefix):
                return True
        return False

    def extract(self, text: str) -> dict[str, BoolWithConfidence]:
        """Analiza el texto y extrae el conjunto completo de señales léxicas.
        
        Args:
            text: Texto libre a analizar (título y descripción combinados).
            
        Returns:
            Un diccionario con las 10 señales como instancias de BoolWithConfidence.
        """
        results = {}
        cleaned_text = text.strip() if text else ""

        for signal_name, regex in self.patterns.items():
            if cleaned_text and self._has_non_negated_match(regex, cleaned_text):
                results[signal_name] = BoolWithConfidence(value=True, confidence=1.0)
            else:
                results[signal_name] = BoolWithConfidence(value=False, confidence=1.0)

        return results
