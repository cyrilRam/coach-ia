from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PACKAGE_ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class DashboardConfig:
    root: Path = PROJECT_ROOT
    season_file: str = "saison-2026-2027.yaml"
    form_directory: str = "forme"
    template_file: Path = PACKAGE_ROOT / "template.html"
    output_file: str = "dashboard/index.html"
    stats_days: int = 365
    minimum_activity_seconds: int = 60
    resting_hr_alert_bpm: int = 56
    hrv_alert_ms: int = 50
    sleep_alert_hours: float = 7.0
    tsb_alert: int = -25

    @property
    def season_path(self) -> Path:
        return self.root / self.season_file

    @property
    def form_path(self) -> Path:
        return self.root / self.form_directory

    @property
    def output_path(self) -> Path:
        return self.root / self.output_file
