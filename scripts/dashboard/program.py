from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from pathlib import Path

from ruamel.yaml import YAML

from dashboard.activities import CompletedActivity
from dashboard.season import SeasonBlock
from dashboard.step_formatter import StepFormatter

DAYS_PER_WEEK = 7
STRENGTH_SPORT = "WeightTraining"


@dataclass(frozen=True)
class PlannedSession:
    sport: str
    name: str
    duration_minutes: int
    description: str
    steps: list[str]

    @property
    def counts_in_volume(self) -> bool:
        return self.sport != STRENGTH_SPORT


@dataclass(frozen=True)
class ProgramDay:
    day: date
    day_number: int
    sessions: list[PlannedSession] = field(default_factory=list)
    activities: list[CompletedActivity] = field(default_factory=list)

    @property
    def planned_minutes(self) -> int:
        return sum(session.duration_minutes for session in self.sessions if session.counts_in_volume)

    @property
    def done_minutes(self) -> int:
        return sum(activity.moving_minutes for activity in self.activities if activity.sport != STRENGTH_SPORT)


@dataclass(frozen=True)
class ProgramWeek:
    number: int
    days: list[ProgramDay]

    def to_dict(self) -> dict[str, object]:
        return {"number": self.number, "start": self.days[0].day, "end": self.days[-1].day, "planned_minutes": sum(day.planned_minutes for day in self.days), "done_minutes": sum(day.done_minutes for day in self.days), "days": [self._day_to_dict(day) for day in self.days]}

    @staticmethod
    def _day_to_dict(day: ProgramDay) -> dict[str, object]:
        return {"date": day.day, "day_number": day.day_number, "sessions": [asdict(session) for session in day.sessions], "activities": [activity.to_dict() for activity in day.activities]}


class ProgramBuilder:
    def __init__(self, root: Path, step_formatter: StepFormatter, activities_by_day: dict[str, list[CompletedActivity]]) -> None:
        self.root = root
        self.step_formatter = step_formatter
        self.activities_by_day = activities_by_day
        self.yaml = YAML(typ="safe")

    def build(self, block: SeasonBlock) -> dict[str, object] | None:
        if block.file is None or not (self.root / block.file).exists():
            return None
        raw = self.yaml.load((self.root / block.file).read_text(encoding="utf-8"))
        sessions_by_number = self._sessions_by_day_number(raw.get("seances", []))
        total_days = int(raw.get("duree_semaines", 0)) * DAYS_PER_WEEK
        days = [self._day(block.start, number, sessions_by_number.get(number, [])) for number in range(1, total_days + 1)]
        weeks = [ProgramWeek(index // DAYS_PER_WEEK + 1, days[index:index + DAYS_PER_WEEK]) for index in range(0, len(days), DAYS_PER_WEEK)]
        return {"block_id": block.id, "name": raw.get("nom", block.name), "objective": raw.get("objectif", block.objective), "focus": list(raw.get("focus", [])), "validated_on": raw.get("valide_le"), "weeks": [week.to_dict() for week in weeks]}

    def _sessions_by_day_number(self, raw_sessions: list[dict]) -> dict[int, list[PlannedSession]]:
        sessions: dict[int, list[PlannedSession]] = {}
        for raw in raw_sessions:
            sessions.setdefault(int(raw["jour"]), []).append(self._to_session(raw))
        return sessions

    def _to_session(self, raw: dict) -> PlannedSession:
        return PlannedSession(sport=raw.get("sport", "Ride"), name=raw.get("nom", ""), duration_minutes=int(raw.get("duree_min") or 0), description=str(raw.get("description", "")).strip(), steps=self.step_formatter.format_all(raw))

    def _day(self, block_start: date, number: int, sessions: list[PlannedSession]) -> ProgramDay:
        day = block_start + timedelta(days=number - 1)
        return ProgramDay(day, number, sessions, self.activities_by_day.get(day.isoformat(), []))
