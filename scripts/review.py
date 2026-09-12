"""Compare les seances planifiees d'un bloc a ce qui a reellement ete fait.

C'est la boucle que la plupart des coachs IA du marche n'ont pas : ils
construisent le bloc suivant sans jamais savoir si le precedent a ete suivi.
Sortie volontairement factuelle — l'interpretation se fait en conversation.

    python scripts/review.py blocs/bloc-01.yaml --debut 2026-10-06
"""

from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path

from ruamel.yaml import YAML

from sync import charger

ROOT = Path(__file__).resolve().parent.parent
yaml = YAML(typ="safe")

TOLERANCE_DUREE = 0.20  # 20 % d'ecart accepte avant de signaler


def parse_jour(valeur: str | None) -> date | None:
    if not valeur:
        return None
    try:
        return date.fromisoformat(valeur[:10])
    except ValueError:
        return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bloc", type=Path)
    parser.add_argument("--debut", required=True, help="date du jour 1 (AAAA-MM-JJ)")
    args = parser.parse_args()

    chemin = args.bloc if args.bloc.is_absolute() else ROOT / args.bloc
    bloc = yaml.load(chemin.read_text(encoding="utf-8"))
    debut = date.fromisoformat(args.debut)
    fin = debut + timedelta(days=bloc.get("duree_semaines", 4) * 7)

    activites = charger("activities")
    reelles = [
        a for a in activites
        if (j := parse_jour(a.get("start_date_local") or a.get("start_date")))
        and debut <= j < fin
    ]
    par_jour: dict[date, list] = {}
    for a in reelles:
        j = parse_jour(a.get("start_date_local") or a.get("start_date"))
        par_jour.setdefault(j, []).append(a)

    print(f"Bloc : {bloc.get('nom')} ({bloc['id']})")
    print(f"Periode : {debut} -> {fin - timedelta(days=1)}\n")

    honorees = manquees = 0
    lignes = []

    for seance in bloc.get("seances", []):
        jour = debut + timedelta(days=seance["jour"] - 1)
        prevue_min = seance.get("duree_min") or 0
        faites = par_jour.get(jour, [])

        if not faites:
            manquees += 1
            lignes.append(f"  {jour}  MANQUEE   {seance['nom']}")
            continue

        honorees += 1
        reelle_min = sum(a.get("moving_time") or 0 for a in faites) / 60
        charge = sum(a.get("icu_training_load") or 0 for a in faites)
        ecart = (reelle_min - prevue_min) / prevue_min if prevue_min else 0
        marqueur = "ECART " if abs(ecart) > TOLERANCE_DUREE else "ok    "
        lignes.append(
            f"  {jour}  {marqueur}    {seance['nom']} — "
            f"{reelle_min:.0f} min prevu {prevue_min} ({ecart:+.0%}), charge {charge:.0f}"
        )

    print("\n".join(lignes))

    total = honorees + manquees
    charge_totale = sum(a.get("icu_training_load") or 0 for a in reelles)
    hors_plan = len(reelles) - sum(len(par_jour.get(
        debut + timedelta(days=s["jour"] - 1), [])) for s in bloc.get("seances", []))

    print(f"\nCompliance : {honorees}/{total} seances "
          f"({honorees / total:.0%})" if total else "\nAucune seance planifiee")
    print(f"Charge totale sur le bloc : {charge_totale:.0f}")
    if hors_plan > 0:
        print(f"Activites hors plan : {hors_plan}")
    print("\nA reporter dans forme/ : ce qui a ete decale et pourquoi.")


if __name__ == "__main__":
    main()
