"""Pousse les seances d'un bloc vers le calendrier Intervals.icu.

Seul script qui ECRIT dans Intervals. Dry-run par defaut : rien n'est envoye
tant que --push n'est pas passe explicitement.

L'agent ne retire jamais --dry-run de lui-meme (voir AGENTS.md).

La conversion des cibles en watts se fait ici, a partir du FTP declare dans
athlete.yaml — jamais depuis le FTP estime par Intervals.

    python scripts/push_block.py blocs/bloc-01.yaml --debut 2026-10-06
    python scripts/push_block.py blocs/bloc-01.yaml --debut 2026-10-06 --push
"""

from __future__ import annotations

import argparse
import re
from datetime import date, timedelta
from pathlib import Path

from ruamel.yaml import YAML

from icu_client import IcuClient

ROOT = Path(__file__).resolve().parent.parent
yaml = YAML(typ="safe")

ZONES_DEFAUT = {
    "Z1": (0, 55), "Z2": (56, 75), "Z3": (76, 90),
    "Z4": (91, 105), "Z5": (106, 120), "Z6": (121, 150),
}


def charger_ftp() -> int:
    profil = yaml.load((ROOT / "athlete.yaml").read_text(encoding="utf-8"))
    ftp = profil["seuils"]["ftp"]
    if ftp.get("source") != "declare":
        raise SystemExit(
            "athlete.yaml > seuils.ftp.source doit rester 'declare'. "
            "Le FTP ne se calcule pas automatiquement."
        )
    return int(ftp["valeur_w"])


def bornes_pct(cible) -> tuple[int, int]:
    """'88-93%' -> (88, 93) ; 'Z3' -> (76, 90) ; '90%' -> (90, 90)."""
    if cible is None:
        return (0, 0)
    texte = str(cible).strip().upper()
    if texte in ZONES_DEFAUT:
        return ZONES_DEFAUT[texte]
    nombres = [int(n) for n in re.findall(r"\d+", texte)]
    if not nombres:
        return (0, 0)
    return (nombres[0], nombres[-1])


def en_watts(cible, ftp: int) -> tuple[int, int]:
    bas, haut = bornes_pct(cible)
    return (round(ftp * bas / 100), round(ftp * haut / 100))


def etapes(seance: dict, ftp: int) -> list[str]:
    """Traduit les intervalles YAML en syntaxe de workout Intervals.icu.

    Deterministe et isole : c'est le futur serialiseur C#. Aucun LLM ne doit
    jamais ecrire cette syntaxe directement.
    """
    lignes = []
    for it in seance.get("intervalles", []):
        bas, haut = en_watts(it.get("cible"), ftp)
        
        if "duree_s" in it:
            duree_str = f"{it['duree_s']}s"
        elif "duree_sec" in it:
            duree_str = f"{it['duree_sec']}s"
        else:
            duree_str = f"{it.get('duree_min', 0)}m"

        reps = it.get("repetitions", 1)
        cadence = f" {it['cadence']}rpm" if it.get("cadence") else ""

        if it.get("recup_s"):
            recup_str = f"{it['recup_s']}s"
        elif it.get("recup_sec"):
            recup_str = f"{it['recup_sec']}s"
        elif it.get("recup_min"):
            recup_str = f"{it['recup_min']}m"
        else:
            recup_str = None

        if reps > 1:
            lignes.append("")
            lignes.append(f"{reps}x")
            lignes.append(f"- {duree_str} {bas}-{haut}W{cadence}")
            if recup_str:
                r_bas, r_haut = en_watts(it.get("recup_cible"), ftp)
                lignes.append(f"- {recup_str} {r_bas}-{r_haut}W")
            lignes.append("")
        else:
            lignes.append(f"- {duree_str} {bas}-{haut}W{cadence}")
            if recup_str:
                r_bas, r_haut = en_watts(it.get("recup_cible"), ftp)
                lignes.append(f"- {recup_str} {r_bas}-{r_haut}W")
    return lignes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bloc", type=Path)
    parser.add_argument("--debut", required=True, help="date du jour 1 (AAAA-MM-JJ)")
    parser.add_argument("--push", action="store_true",
                        help="envoie reellement vers Intervals.icu")
    args = parser.parse_args()

    chemin = args.bloc if args.bloc.is_absolute() else ROOT / args.bloc
    bloc = yaml.load(chemin.read_text(encoding="utf-8"))
    debut = date.fromisoformat(args.debut)
    ftp = charger_ftp()

    print(f"Bloc : {bloc.get('nom')} — depart {debut} — FTP declare {ftp} W")
    print("MODE DRY-RUN, rien ne sera envoye\n" if not args.push
          else "MODE PUSH, les seances seront creees\n")

    payloads = []
    for seance in bloc.get("seances", []):
        jour = debut + timedelta(days=seance["jour"] - 1)
        corps = etapes(seance, ftp)
        description = seance.get("description", "")
        payloads.append({
            "start_date_local": f"{jour.isoformat()}T00:00:00",
            "category": "WORKOUT",
            "type": seance.get("sport", "Ride"),
            "name": seance["nom"],
            "description": (description + "\n\n" + "\n".join(corps)).strip(),
            "moving_time": (seance.get("duree_min") or 0) * 60,
        })
        print(f"{jour}  {seance.get('sport', 'Ride'):<5} {seance['nom']} "
              f"({seance.get('duree_min')} min)")
        for ligne in corps:
            print(f"       {ligne}")
        print()

    if not args.push:
        print(f"{len(payloads)} seances pretes. Relance avec --push pour envoyer.")
        return

    client = IcuClient()
    for payload in payloads:
        client.create_event(payload)
        print(f"cree : {payload['start_date_local'][:10]} {payload['name']}")
    print(f"\n{len(payloads)} seances poussees sur le calendrier Intervals.")


if __name__ == "__main__":
    main()
