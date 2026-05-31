"""Extractor determinista de señales léxicas y semánticas basado en expresiones regulares."""

from __future__ import annotations

import re
from typing import Any

from contracts import Accesibilidad, BoolWithConfidence, IntWithConfidence


class SignalExtractor:
    """Clase encargada de analizar texto libre y extraer señales léxicas y operativas.
    
    Cada señal léxica se devuelve como BoolWithConfidence. Soporta resiliencia
    a acentos, expresiones multilingües (español/inglés) y extracción semántica compleja
    para variables de Castilla y León.
    """

    def __init__(self) -> None:
        # Expresiones regulares optimizadas (bilingües y con resiliencia a acentos/tildes)
        self.patterns = {
            "signal_fallecido": re.compile(
                r"\b(muert[oa]s?|fallecid[oa]s?|cad[aá]ver(es)?|difunt[oa]s?|[oó]bitos?|"
                r"finad[oa]s?|muerte|decesos?|pcr|parada\s+cardio|fallece(n)?|"
                r"dead|death|deceased|corpse|fatal|killed|casualt(y|ies))\b",
                re.IGNORECASE,
            ),
            "signal_herido_grave": re.compile(
                r"\b(grave(s)?|cr[ií]tic[oa]s?|inconsciente?s?|hemorragia\s+masiva|amputaci[oó]n(es)?|"
                r"fractura\s+abierta|infarto|dolor\s+pecho|ahogamiento|asfixia|quemadura\s+grave|coma|"
                r"no\s+respira|inconsciencia|critical|heavy\s+bleeding|amputation|open\s+fracture|"
                r"heart\s+attack|chest\s+pain|asphyxia|severe\s+burn|not\s+breathing|unconscious(ness)?|severe\s+injur(y|ies))\b",
                re.IGNORECASE,
            ),
            "signal_atrapado": re.compile(
                r"\b(atrapad[oa]s?|excarcelar|excarcelaci[oó]n|no\s+puede\s+salir|prensad[oa]s?|"
                r"aplastad[oa]s?|encerrad[oa]s?|atrapamiento(s)?|trapped|stuck|pinned|crushed|"
                r"cannot\s+get\s+out|extrication)\b",
                re.IGNORECASE,
            ),
            "signal_intoxicacion": re.compile(
                r"\b(intoxicaci[oó]n|intoxicad[oa]s?|gases?|humos?|co|mon[oó]xido|qu[ií]mic[oa]s?|"
                r"olor\s+fuerte|vertidos?|fuga\s+gas|inhalaci[oó]n\s+humo|pesticidas?|venenos?|"
                r"poisoning|intoxicated|monoxide|chemical(s)?|strong\s+smell|spill(s)?|"
                r"gas\s+leak|smoke\s+inhalation|poison)\b",
                re.IGNORECASE,
            ),
            "signal_varias_llamadas": re.compile(
                r"\b(varias\s+llamadas|m[uú]ltiples\s+avisos|muchas\s+llamadas|segundo\s+aviso|"
                r"reiteradas\s+llamadas|reiterados\s+avisos|multiple\s+calls|several\s+calls|"
                r"many\s+calls|second\s+notice|repeated\s+calls)\b",
                re.IGNORECASE,
            ),
            "signal_incendio": re.compile(
                r"\b(incendios?|fuegos?|quemas?|deflagraci[oó]n(es)?|llamas?|forestal(es)?|conatos?|"
                r"arde(n)?|ardiendo|quemando|chispas?|explosiones?|fire(s)?|blaze(s)?|burn(s)?|"
                r"burning|wildfire(s)?|flame(s)?|explosion(s)?|spark(s)?)\b",
                re.IGNORECASE,
            ),
            "signal_accidente_trafico": re.compile(
                r"\b(accidentes?|coches?|colisi[oó]n(es)?|choques?|atropellos?|vuelcos?|cami[oó]n(es)?|"
                r"motos?|veh[ií]culos?|calzada|carreteras?|autov[ií]as?|accident(s)?|car(s)?|"
                r"collision(s)?|crash(es)?|run\s+over|rollover|truck(s)?|motorcycle(s)?|"
                r"vehicle(s)?|road(s)?|highway(s)?)\b",
                re.IGNORECASE,
            ),
            "signal_rescate": re.compile(
                r"\b(rescates?|rescatar|auxilios?|socorros?|evacuaci[oó]n(es)?|b[uú]squedas?|"
                r"atrapado\s+monta[ñn]a|atrapado\s+r[ií]o|helic[oó]pteros?|salvamentos?|"
                r"rescue(s)?|help|aid|evacuation(s)?|search|helicopter(s)?|salvage)\b",
                re.IGNORECASE,
            ),
            "signal_meteo_inundacion": re.compile(
                r"\b(inundaci[oó]n(es)?|inundad[oa]s?|riadas?|desbordamientos?|agua\s+acumulada|"
                r"tormentas?|granizos?|vientos?\s+fuerte(s)?|temporales?|lluvias?\s+intensa(s)?|"
                r"flood(s)?|flooded|overflow|storm(s)?|hail|heavy\s+rain(s)?)\b",
                re.IGNORECASE,
            ),
            "riesgo_vital_textual": re.compile(
                r"\b(riesgo\s+vital|peligro\s+muerte|se\s+muere|parada\s+respiratoria|no\s+responde|"
                r"asfixi[aá]ndose|ahog[aá]ndose|c[oó]digo\s+rojo|cr[ií]tico|vida\s+peligro|"
                r"life\s+risk|life-threatening|danger\s+of\s+death|dying|respiratory\s+arrest|"
                r"not\s+responding|suffocating|drowning|code\s+red)\b",
                re.IGNORECASE,
            ),
        }

        # Patrones avanzados para extracción semántica
        self.vuln_pattern = re.compile(
            r"\b(niñ[oa]s?|beb[eé]s?|menor(es)?(\s+de\s+edad)?|infantil(es)?|colegio|guarder[ií]a|"
            r"parque\s+infantil|ancian[oa]s?|abuel[oa]s?|personas?\s+mayores?|octogenari[oa]s?|"
            r"residencia\s+de\s+ancianos|geri[aá]trico|embarazada?s?|minusv[aá]lid[oa]s?|"
            r"discapacitad[oa]s?|silla\s+de\s+ruedas|kids?|bab[iy]s?|children|child|toddler|"
            r"minor(s)?|school|nursery|elderly|old\s+person|grandparents?|grandmother|"
            r"grandfather|nursing\s+home|geriatric|pregnant|disabled|wheelchair)\b",
            re.IGNORECASE,
        )

        self.critical_loc_pattern = re.compile(
            r"\b(colegio|escuela|hospital|ambulatorio|cl[ií]nica|residencia|centro\s+comercial|"
            r"aeropuerto|estaci[oó]n|discoteca|bar\s+concurrido|hotel|t[uú]nel|puente|"
            r"gasolinera|pol[ií]gono|qu[ií]mica|refiner[ií]a|f[aá]brica|autov[ií]a|autopista|"
            r"v[ií]a\s+f[eé]rrea|tren|school|hospital|clinic|shopping\s+mall|airport|station|"
            r"nightclub|busy\s+bar|hotel|tunnel|bridge|gas\s+station|industrial\s+park|"
            r"chemical\s+plant|refinery|factory|highway|railway|train)\b",
            re.IGNORECASE,
        )

        self.access_low_pattern = re.compile(
            r"\b(nieve|hielo|temporal|ventisca|monta[ñn]a|pico|barranco|acceso\s+dif[ií]cil|"
            r"dif[ií]cil\s+acceso|sendero|inundaci[oó]n|desprendimiento|barro|snow|ice|"
            r"blizzard|mountain|cliff|difficult\s+access|trail|mud|landslide)\b",
            re.IGNORECASE,
        )

        self.access_medium_pattern = re.compile(
            r"\b(lluvia\s+fuerte|niebla|camino\s+de\s+tierra|zona\s+rural|carretera\s+secundaria|"
            r"heavy\s+rain|fog|dirt\s+road|rural\s+area|secondary\s+road)\b",
            re.IGNORECASE,
        )

        self.access_high_pattern = re.compile(
            r"\b(casco\s+urbano|centro\s+ciudad|avenida|autov[ií]a|autopista|calle\s+principal|"
            r"city\s+center|downtown|highway|main\s+street)\b",
            re.IGNORECASE,
        )

        self.propagation_pattern = re.compile(
            r"\b(viento\s+fuerte|rachas|monte|pinar|f[aá]brica|gasolina|gas|casas\s+colindantes|"
            r"edificio\s+de\s+viviendas|propagaci[oó]n|combustible|strong\s+wind|gusts|"
            r"forest|dry\s+grass|adjacent|fuel|propagation|spread)\b",
            re.IGNORECASE,
        )

        # Mapeo semántico de palabras numéricas a enteros
        self.number_mapping = {
            "un": 1, "una": 1, "uno": 1, "one": 1,
            "dos": 2, "two": 2,
            "tres": 3, "three": 3,
            "cuatro": 4, "four": 4,
            "cinco": 5, "five": 5,
            "seis": 6, "six": 6,
            "siete": 7, "seven": 7,
            "ocho": 8, "eight": 8,
            "nueve": 9, "nine": 9,
            "diez": 10, "ten": 10,
        }
        
        # Expresión regular para capturar números escritos o dígitos
        num_pattern_str = r"\b(\d+|" + "|".join(self.number_mapping.keys()) + r")\b"
        damage_words = (
            r"(herid[oa]s?|lesionad[oa]s?|afectad[oa]s?|atrapad[oa]s?|fallecid[oa]s?|"
            r"muert[oa]s?|inconsciente?s?|persona?s?|v[ií]ctima?s?|victima?s?|"
            r"injured|hurt|dead|trapped|casualt(y|ies)|people|person)"
        )
        
        # Patrones de proximidad: "3 heridos" o "heridos: 3" o "tres personas"
        self.victim_count_patterns = [
            re.compile(rf"{num_pattern_str}\s+(?:de\s+)?{damage_words}", re.IGNORECASE),
            re.compile(rf"{damage_words}\s+(?:de\s+)?{num_pattern_str}", re.IGNORECASE),
            re.compile(rf"{damage_words}\s*:\s*{num_pattern_str}", re.IGNORECASE),
        ]
        
        self.several_pattern = re.compile(
            r"\b(varios|varias|m[uú]ltiples|decena|docena|several|multiple|dozen)\b", 
            re.IGNORECASE
        )

    def extract(self, text: str) -> dict[str, BoolWithConfidence]:
        """Analiza el texto y extrae el conjunto completo de 10 señales léxicas obligatorias.
        
        Args:
            text: Texto libre a analizar (título y descripción combinados).
            
        Returns:
            Un diccionario con las 10 señales como instancias de BoolWithConfidence.
        """
        results = {}
        cleaned_text = text.strip() if text else ""

        for signal_name, regex in self.patterns.items():
            if cleaned_text and regex.search(cleaned_text):
                results[signal_name] = BoolWithConfidence(value=True, confidence=1.0)
            else:
                results[signal_name] = BoolWithConfidence(value=False, confidence=1.0)

        return results

    def extract_vulnerable_population(self, text: str) -> BoolWithConfidence:
        """Determina si en el texto se menciona población vulnerable.
        
        Args:
            text: Texto de entrada.
            
        Returns:
            BoolWithConfidence validado.
        """
        if text and self.vuln_pattern.search(text):
            return BoolWithConfidence(value=True, confidence=0.90)
        return BoolWithConfidence(value=False, confidence=0.50)

    def extract_critical_location(self, text: str) -> BoolWithConfidence:
        """Determina si el incidente ocurre en un emplazamiento crítico de infraestructura o afluencia.
        
        Args:
            text: Texto de entrada.
            
        Returns:
            BoolWithConfidence validado.
        """
        if text and self.critical_loc_pattern.search(text):
            return BoolWithConfidence(value=True, confidence=0.90)
        return BoolWithConfidence(value=False, confidence=0.50)

    def extract_accessibility(self, text: str) -> tuple[Accesibilidad, float]:
        """Infiere las condiciones de accesibilidad para recursos de emergencia.
        
        Args:
            text: Texto de entrada.
            
        Returns:
            Tupla (Accesibilidad, confianza).
        """
        if not text:
            return Accesibilidad.DESCONOCIDA, 0.50

        if self.access_low_pattern.search(text):
            return Accesibilidad.BAJA, 0.90
        elif self.access_medium_pattern.search(text):
            return Accesibilidad.MEDIA, 0.80
        elif self.access_high_pattern.search(text):
            return Accesibilidad.ALTA, 0.80
        
        return Accesibilidad.DESCONOCIDA, 0.50

    def extract_propagation_risk(self, text: str, is_incendio: bool) -> BoolWithConfidence:
        """Infiere el riesgo de propagación basado en las condiciones descritas y el tipo de incidente.
        
        Args:
            text: Texto de entrada.
            is_incendio: True si la señal de incendio está activa.
            
        Returns:
            BoolWithConfidence validado.
        """
        has_prop_keywords = bool(text and self.propagation_pattern.search(text))
        
        if is_incendio:
            # En un incendio, la presencia de palabras de propagación da una confianza absoluta
            return BoolWithConfidence(value=True, confidence=0.95 if has_prop_keywords else 0.80)
        
        if has_prop_keywords:
            return BoolWithConfidence(value=True, confidence=0.75)
            
        return BoolWithConfidence(value=False, confidence=0.50)

    def extract_estimated_victims(self, text: str, has_fatal_or_injured: bool) -> IntWithConfidence:
        """Analiza lingüísticamente el texto para estimar el número de víctimas heridas o fallecidas.
        
        Args:
            text: Texto libre del incidente.
            has_fatal_or_injured: True si hay señales de fallecido o herido grave activas.
            
        Returns:
            IntWithConfidence con el número estimado de víctimas (-1 si es desconocido).
        """
        if not text:
            return IntWithConfidence(value=1 if has_fatal_or_injured else -1, confidence=0.50)

        # 1. Intentar buscar patrones de proximidad: "3 heridos" o "dos fallecidos"
        for pattern in self.victim_count_patterns:
            for match in pattern.finditer(text):
                # Extraer el grupo numérico
                for val in match.groups():
                    if not val:
                        continue
                    # Si es dígito
                    if val.isdigit():
                        num = int(val)
                        if 0 <= num <= 50:
                            return IntWithConfidence(value=num, confidence=0.90)
                    # Si es palabra de mapeo
                    cleaned_val = val.lower()
                    if cleaned_val in self.number_mapping:
                        return IntWithConfidence(value=self.number_mapping[cleaned_val], confidence=0.85)

        # 2. Si se encuentran palabras vagas como "varios heridos" o "múltiples personas"
        if self.several_pattern.search(text):
            return IntWithConfidence(value=3, confidence=0.75)  # Estimación representativa razonable para Castilla y León

        # 3. Fallback: si hay señales deterministas de heridos o fallecidos, estimar al menos 1
        if has_fatal_or_injured:
            return IntWithConfidence(value=1, confidence=0.65)

        return IntWithConfidence(value=-1, confidence=0.50)
