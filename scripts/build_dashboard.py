from __future__ import annotations

import argparse
import webbrowser
from datetime import date

from dashboard import ActivityRepository, DashboardConfig, DashboardService, FormWeekRepository, HealthRepository, HtmlRenderer, ProgramBuilder, SeasonRepository, StepFormatter
from push_block import charger_ftp


def create_service(config: DashboardConfig) -> DashboardService:
    program_builder = ProgramBuilder(config.root, StepFormatter(charger_ftp()), ActivityRepository(config.minimum_activity_seconds).by_day())
    return DashboardService(config, SeasonRepository(config.season_path), program_builder, HealthRepository(config.stats_days), FormWeekRepository(config.form_path), HtmlRenderer(config.template_file))


def main() -> None:
    parser = argparse.ArgumentParser(description="Genere le tableau de bord local (programme + stats) a partir des YAML et du cache.")
    parser.add_argument("--ouvrir", action="store_true", help="ouvre la page dans le navigateur apres generation")
    args = parser.parse_args()
    output = create_service(DashboardConfig()).build(date.today())
    print(f"Tableau de bord genere : {output}")
    if args.ouvrir:
        webbrowser.open(f"file://{output}")


if __name__ == "__main__":
    main()
