from __future__ import annotations

from push_block import SPORTS_CIBLE_FC, en_watts

STEP_LABELS = {"echauffement": "Échauffement", "continu": "Continu", "effort": "Effort", "retour_calme": "Retour au calme"}
HEART_RATE_ZONE_SUFFIX = "FC"


class StepFormatter:
    def __init__(self, ftp: int) -> None:
        self.ftp = ftp

    def format_all(self, session: dict) -> list[str]:
        heart_rate_target = session.get("sport") in SPORTS_CIBLE_FC
        return [self._format(step, heart_rate_target) for step in session.get("intervalles", [])]

    def _format(self, step: dict, heart_rate_target: bool) -> str:
        label = STEP_LABELS.get(step.get("type", ""), step.get("type", ""))
        effort = f"{self._duration(step)} @ {self._target(step.get('cible'), heart_rate_target)}"
        repetitions = step.get("repetitions", 1)
        cadence = f" à {step['cadence']} rpm" if step.get("cadence") else ""
        recovery = self._recovery(step, heart_rate_target)
        prefix = f"{repetitions} × " if repetitions > 1 else ""
        return f"{label} : {prefix}{effort}{cadence}{recovery}"

    def _recovery(self, step: dict, heart_rate_target: bool) -> str:
        if step.get("recup_min"):
            return f" · récup {step['recup_min']}' @ {self._target(step.get('recup_cible'), heart_rate_target)}"
        if step.get("recup_s"):
            return f" · récup {step['recup_s']}s @ {self._target(step.get('recup_cible'), heart_rate_target)}"
        return ""

    def _target(self, target: object, heart_rate_target: bool) -> str:
        if heart_rate_target:
            return f"{target} {HEART_RATE_ZONE_SUFFIX}"
        low, high = en_watts(target, self.ftp)
        return f"{low}-{high} W ({target})"

    @staticmethod
    def _duration(step: dict) -> str:
        if "duree_s" in step:
            return f"{step['duree_s']}s"
        return f"{step.get('duree_min', 0)}'"
