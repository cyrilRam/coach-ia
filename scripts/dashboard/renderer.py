from __future__ import annotations

import json
from pathlib import Path

DATA_PLACEHOLDER = "__DASHBOARD_DATA__"
SCRIPT_CLOSING_SEQUENCE = "</"
ESCAPED_SCRIPT_CLOSING_SEQUENCE = "<\\/"


class HtmlRenderer:
    def __init__(self, template_path: Path) -> None:
        self.template_path = template_path

    def render(self, payload: dict[str, object]) -> str:
        data = json.dumps(payload, ensure_ascii=False, default=str).replace(SCRIPT_CLOSING_SEQUENCE, ESCAPED_SCRIPT_CLOSING_SEQUENCE)
        return self.template_path.read_text(encoding="utf-8").replace(DATA_PLACEHOLDER, data)
