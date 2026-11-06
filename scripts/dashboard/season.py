from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

from ruamel.yaml import YAML

from dashboard.dates import DateHelper


@dataclass(frozen=True)
class SeasonBlock:
    id: str
    name: str
    start: date
    end: date | None
    objective: str
    rhythm: str
    focus: list[str] = field(default_factory=list)
    target_hours: list[float] = field(default_factory=list)
    file: str | None = None

    def contains(self, day: date) -> bool:
        return self.start <= day and (self.end is None or day <= self.end)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class Race:
    name: str
    date_label: str
    day: date | None
    approximate: bool
    priority: str
    course: str
    profile: str
    notes: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class Season:
    name: str
    blocks: list[SeasonBlock]
    races: list[Race]

    def current_block(self, today: date) -> SeasonBlock | None:
        return next((block for block in self.blocks if block.contains(today)), None)


class SeasonRepository:
    def __init__(self, season_path: Path) -> None:
        self.season_path = season_path
        self.yaml = YAML(typ="safe")

    def load(self) -> Season:
        raw = self.yaml.load(self.season_path.read_text(encoding="utf-8"))
        blocks = [self._to_block(entry) for entry in raw.get("blocs", [])]
        objectives = raw.get("objectifs", {})
        races = [self._to_race(entry) for entry in [objectives.get("principal", {}), *objectives.get("secondaires", [])] if entry]
        return Season(str(raw.get("saison", "")), blocks, sorted(races, key=lambda race: race.day or date.max))

    def _to_block(self, entry: dict) -> SeasonBlock:
        return SeasonBlock(id=entry["id"], name=entry.get("nom", ""), start=DateHelper.parse(entry["du"]), end=DateHelper.parse(entry.get("au")), objective=entry.get("objectif", ""), rhythm=entry.get("rythme", ""), focus=list(entry.get("focus", [])), target_hours=list(entry.get("volume_cible_h", [])), file=entry.get("fichier"))

    def _to_race(self, entry: dict) -> Race:
        label = str(entry.get("date", "")).strip()
        exact = DateHelper.parse(label)
        return Race(name=entry.get("nom", ""), date_label=label, day=exact or DateHelper.approximate(label), approximate=exact is None, priority=str(entry.get("priorite", "")), course=str(entry.get("parcours", "")), profile=str(entry.get("profil", "")), notes=str(entry.get("notes", "")))
