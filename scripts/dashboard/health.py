from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, timedelta
from statistics import mean

from sync import charger

ROLLING_WINDOW_DAYS = 7
SECONDS_PER_HOUR = 3600


@dataclass(frozen=True)
class DailyHealth:
    date: str
    ctl: float | None
    atl: float | None
    tsb: float | None
    resting_hr: int | None
    hrv: float | None
    hrv_rolling: float | None
    sleep_hours: float | None
    sleep_score: float | None


class HealthRepository:
    def __init__(self, days: int) -> None:
        self.days = days

    def daily(self, today: date) -> list[dict[str, object]]:
        oldest = (today - timedelta(days=self.days)).isoformat()
        rows = sorted((raw for raw in charger("wellness") if oldest <= raw.get("id", "") <= today.isoformat()), key=lambda raw: raw["id"])
        return [asdict(self._to_health(rows, index)) for index in range(len(rows))]

    def _to_health(self, rows: list[dict], index: int) -> DailyHealth:
        raw = rows[index]
        ctl = self._rounded(raw.get("ctl"))
        atl = self._rounded(raw.get("atl"))
        tsb = None if ctl is None or atl is None else round(ctl - atl, 1)
        sleep_seconds = raw.get("sleepSecs")
        sleep_hours = None if not sleep_seconds else round(sleep_seconds / SECONDS_PER_HOUR, 2)
        return DailyHealth(date=raw["id"], ctl=ctl, atl=atl, tsb=tsb, resting_hr=raw.get("restingHR"), hrv=raw.get("hrv"), hrv_rolling=self._rolling_hrv(rows, index), sleep_hours=sleep_hours, sleep_score=raw.get("sleepScore"))

    @staticmethod
    def _rolling_hrv(rows: list[dict], index: int) -> float | None:
        window = [raw["hrv"] for raw in rows[max(0, index - ROLLING_WINDOW_DAYS + 1):index + 1] if raw.get("hrv")]
        return round(mean(window), 1) if window else None

    @staticmethod
    def _rounded(value: float | None) -> float | None:
        return None if value is None else round(value, 1)
