from __future__ import annotations

import re
from datetime import date

FRENCH_MONTHS = {"janvier": 1, "fevrier": 2, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6, "juillet": 7, "aout": 8, "août": 8, "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12, "décembre": 12}
DAY_BY_KEYWORD = {"premier": 1, "debut": 1, "début": 1, "2eme": 8, "deuxieme": 8, "mi": 15, "fin": 25}
DEFAULT_DAY_IN_MONTH = 15
MONTH_YEAR_PATTERN = re.compile(r"([a-zéû]+)\s+(\d{4})")


class DateHelper:
    @staticmethod
    def parse(value: object) -> date | None:
        if isinstance(value, date):
            return value
        if not isinstance(value, str):
            return None
        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            return None

    @staticmethod
    def approximate(label: str) -> date | None:
        text = label.lower()
        match = next((found for found in MONTH_YEAR_PATTERN.finditer(text) if found.group(1) in FRENCH_MONTHS), None)
        if match is None:
            return None
        day = next((value for keyword, value in DAY_BY_KEYWORD.items() if re.search(rf"\b{keyword}\b", text[:match.start()])), DEFAULT_DAY_IN_MONTH)
        return date(int(match.group(2)), FRENCH_MONTHS[match.group(1)], day)
