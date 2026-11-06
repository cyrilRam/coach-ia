from __future__ import annotations

import json
from datetime import date, datetime

from dashboard.config import DashboardConfig
from dashboard.form_weeks import FormWeekRepository
from dashboard.health import HealthRepository
from dashboard.program import ProgramBuilder
from dashboard.renderer import HtmlRenderer
from dashboard.season import SeasonRepository
from sync import CACHE

CACHE_REFERENCE_FILE = "wellness.json"


class DashboardService:
    def __init__(self, config: DashboardConfig, season_repository: SeasonRepository, program_builder: ProgramBuilder, health_repository: HealthRepository, form_week_repository: FormWeekRepository, renderer: HtmlRenderer) -> None:
        self.config = config
        self.season_repository = season_repository
        self.program_builder = program_builder
        self.health_repository = health_repository
        self.form_week_repository = form_week_repository
        self.renderer = renderer

    def build(self, today: date) -> str:
        season = self.season_repository.load()
        current = season.current_block(today)
        programs = {block.id: program for block in season.blocks if (program := self.program_builder.build(block)) is not None}
        payload = {"generated_at": datetime.now().isoformat(timespec="minutes"), "cache_fetched_at": self._cache_fetched_at(), "today": today, "season": {"name": season.name, "blocks": [block.to_dict() for block in season.blocks], "races": [race.to_dict() for race in season.races], "current_block_id": current.id if current else None}, "programs": programs, "health": self.health_repository.daily(today), "weeks": self.form_week_repository.weeks(), "thresholds": self._thresholds()}
        html = self.renderer.render(payload)
        self.config.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.config.output_path.write_text(html, encoding="utf-8")
        return str(self.config.output_path)

    def _thresholds(self) -> dict[str, float]:
        return {"resting_hr_alert_bpm": self.config.resting_hr_alert_bpm, "hrv_alert_ms": self.config.hrv_alert_ms, "sleep_alert_hours": self.config.sleep_alert_hours, "tsb_alert": self.config.tsb_alert}

    @staticmethod
    def _cache_fetched_at() -> str | None:
        path = CACHE / CACHE_REFERENCE_FILE
        return json.loads(path.read_text(encoding="utf-8"))["meta"].get("recupere_a") if path.exists() else None
