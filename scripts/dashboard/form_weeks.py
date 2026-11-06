from __future__ import annotations

from pathlib import Path

from ruamel.yaml import YAML

WEEK_FILE_PATTERN = "*-W*.yaml"
MEASURE_FIELDS = ("heures", "charge_totale", "distance_km", "denivele_m", "seances", "ctl_fin", "atl_fin", "tsb_fin", "ramp_rate", "sommeil_moyen_h", "hrv_moyenne", "fc_repos_moyenne")


class FormWeekRepository:
    def __init__(self, form_path: Path) -> None:
        self.form_path = form_path
        self.yaml = YAML(typ="safe")

    def weeks(self) -> list[dict[str, object]]:
        return [self._to_week(path) for path in sorted(self.form_path.glob(WEEK_FILE_PATTERN))]

    def _to_week(self, path: Path) -> dict[str, object]:
        raw = self.yaml.load(path.read_text(encoding="utf-8")) or {}
        measures = raw.get("mesures") or {}
        analysis = raw.get("analyse_coach") or {}
        return {"week": str(raw.get("semaine", path.stem)), "start": raw.get("du"), "end": raw.get("au"), "measures_updated_on": measures.get("maj"), **{field: measures.get(field) for field in MEASURE_FIELDS}, "coach_updated_on": analysis.get("maj"), "coach_decision": analysis.get("decision")}
