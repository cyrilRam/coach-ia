from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass

from sync import charger


@dataclass(frozen=True)
class CompletedActivity:
    name: str
    sport: str
    moving_minutes: int
    load: int | None
    elevation_m: int | None
    normalized_power_w: int | None
    average_hr_bpm: int | None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class ActivityRepository:
    def __init__(self, minimum_activity_seconds: int) -> None:
        self.minimum_activity_seconds = minimum_activity_seconds

    def by_day(self) -> dict[str, list[CompletedActivity]]:
        activities: dict[str, list[CompletedActivity]] = defaultdict(list)
        for raw in sorted(charger("activities"), key=lambda item: item.get("start_date_local", "")):
            if (raw.get("moving_time") or 0) >= self.minimum_activity_seconds:
                activities[raw["start_date_local"][:10]].append(self._to_activity(raw))
        return activities

    def _to_activity(self, raw: dict) -> CompletedActivity:
        return CompletedActivity(name=raw.get("name", ""), sport=raw.get("type", ""), moving_minutes=round((raw.get("moving_time") or 0) / 60), load=raw.get("icu_training_load"), elevation_m=self._rounded(raw.get("total_elevation_gain")), normalized_power_w=raw.get("icu_weighted_avg_watts"), average_hr_bpm=raw.get("average_heartrate"))

    @staticmethod
    def _rounded(value: float | None) -> int | None:
        return None if value is None else round(value)
