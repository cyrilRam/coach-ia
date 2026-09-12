"""Genere la section "mesures" d'un fichier forme/AAAA-Wxx.yaml.

Ecrit uniquement les chiffres. La section "ressenti" est preservee telle quelle
si le fichier existe deja : elle appartient a Lena, le script n'y touche jamais.

A lancer le dimanche soir, ou en cron. Sans le ressenti ecrit a la main, le
coach n'a que des chiffres — c'est exactement ce qu'on reproche aux outils du
marche.
"""

from __future__ import annotations
from sync import charger, assurer
import argparse
from datetime import date, datetime, timedelta
from pathlib import Path

from ruamel.yaml import YAML

from sync import charger

ROOT = Path(__file__).resolve().parent.parent
FORME = ROOT / "forme"

yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)

GABARIT = """\
# Une semaine = un fichier. Nommage en semaines ISO.
# Section "mesures" : generee par scripts/weekly.py, ne pas editer a la main.
# Section "ressenti" : saisie manuelle, l'agent n'y ecrit jamais.
# Section "analyse_coach" : analyse hebdomadaire formulee par l'IA et conservee.

semaine: {semaine}
du: {du}
au: {au}

mesures: {{}}

# saisie manuelle
ressenti:
  global:
  jambes:
  motivation:
  sommeil:
  seances_manquees: []
  imprevus:
  notes:

adaptations: []

analyse_coach:
  maj: null
  synthese: null
  decision: null
"""


def bornes(semaine: str) -> tuple[date, date]:
    annee, num = semaine.split("-W")
    lundi = date.fromisocalendar(int(annee), int(num), 1)
    return lundi, lundi + timedelta(days=6)


def semaine_courante(decalage: int = -1) -> str:
    """Par defaut la semaine ecoulee, pas celle en cours."""
    ref = date.today() + timedelta(weeks=decalage)
    a, n, _ = ref.isocalendar()
    return f"{a}-W{n:02d}"


def parse_jour(valeur: str | None) -> date | None:
    if not valeur:
        return None
    try:
        return date.fromisoformat(valeur[:10])
    except ValueError:
        return None


def moyenne(valeurs: list) -> float | None:
    reels = [v for v in valeurs if isinstance(v, (int, float))]
    return round(sum(reels) / len(reels), 1) if reels else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--semaine", default=semaine_courante())
    parser.add_argument("--no-sync", action="store_true",
                        help="utilise le cache tel quel, sans le rafraichir")
    args = parser.parse_args()

    if not args.no_sync:
        assurer(jours=60, max_age_h=6)

    du, au = bornes(args.semaine)
    activites = charger("activities")
    wellness = charger("wellness")

    dans_semaine = [
        a for a in activites
        if (j := parse_jour(a.get("start_date_local") or a.get("start_date")))
        and du <= j <= au
    ]
    jours = [w for w in wellness if (j := parse_jour(w.get("id"))) and du <= j <= au]
    dernier = max(jours, key=lambda w: w["id"]) if jours else {}

    secondes = sum(a.get("moving_time") or 0 for a in dans_semaine)
    ctl = dernier.get("ctl")
    atl = dernier.get("atl")

    mesures = {
        "maj": date.today().isoformat(),
        "ctl_fin": round(ctl, 1) if isinstance(ctl, (int, float)) else None,
        "atl_fin": round(atl, 1) if isinstance(atl, (int, float)) else None,
        "tsb_fin": round(ctl - atl, 1) if isinstance(ctl, (int, float))
                   and isinstance(atl, (int, float)) else None,
        "ramp_rate": dernier.get("rampRate"),
        "charge_totale": int(round(sum(a.get("icu_training_load") or 0
                                       for a in dans_semaine))),
        "heures": round(secondes / 3600, 1),
        "distance_km": int(round(sum((a.get("distance") or 0) / 1000
                                     for a in dans_semaine))),
        "denivele_m": int(round(sum(a.get("total_elevation_gain") or 0
                                    for a in dans_semaine))),
        "seances": len(dans_semaine),
        "sommeil_moyen_h": (round(s / 3600, 1)
                            if (s := moyenne([w.get("sleepSecs") for w in jours]))
                            else None),
        "hrv_moyenne": moyenne([w.get("hrv") for w in jours]),
        "fc_repos_moyenne": moyenne([w.get("restingHR") for w in jours]),
    }

    FORME.mkdir(exist_ok=True)
    chemin = FORME / f"{args.semaine}.yaml"
    if not chemin.exists():
        chemin.write_text(
            GABARIT.format(semaine=args.semaine, du=du.isoformat(), au=au.isoformat()),
            encoding="utf-8",
        )

    with chemin.open(encoding="utf-8") as f:
        doc = yaml.load(f)
    doc["mesures"] = mesures
    with chemin.open("w", encoding="utf-8") as f:
        yaml.dump(doc, f)

    print(f"{chemin.name} : {mesures['seances']} seances, {mesures['heures']} h, "
          f"charge {mesures['charge_totale']}, CTL {mesures['ctl_fin']}")
    if mesures["hrv_moyenne"] is None:
        print("HRV absente cette semaine — capteur non porte, ou pas encore de "
              "capteur nocturne.")
    print("\nA completer a la main : section 'ressenti'.")


if __name__ == "__main__":
    main()
