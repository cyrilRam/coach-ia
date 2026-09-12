"""Recupere activites et wellness depuis Intervals.icu vers data/cache/.

Separe la recuperation du calcul : on telecharge une fois, on recalcule autant
qu'on veut sans retaper l'API. Indispensable quand on itere sur la formule de
PPR ou d'empreinte de volume.

Le cache stocke les payloads BRUTS, sans transformation. C'est le meme principe
que le stockage jsonb cote base : on ne perd rien, on extrait ensuite.

    python scripts/sync.py                 # 365 derniers jours
    python scripts/sync.py --jours 1095    # 3 ans
"""

from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from pathlib import Path

from icu_client import IcuClient

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "cache"


def dump(nom: str, data, meta: dict) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    chemin = CACHE / f"{nom}.json"
    chemin.write_text(
        json.dumps({"meta": meta, "data": data}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return chemin


def charger(nom: str):
    """Utilise par les autres scripts pour relire le cache."""
    chemin = CACHE / f"{nom}.json"
    if not chemin.exists():
        raise FileNotFoundError(
            f"{chemin} absent. Lance d'abord : python scripts/sync.py"
        )
    return json.loads(chemin.read_text(encoding="utf-8"))["data"]

from datetime import datetime


def age_cache_heures() -> float | None:
    """Age du cache en heures, None s'il n'existe pas."""
    chemin = CACHE / "activities.json"
    if not chemin.exists():
        return None
    meta = json.loads(chemin.read_text(encoding="utf-8"))["meta"]
    horodatage = meta.get("recupere_a") or meta.get("recupere_le")
    try:
        ref = datetime.fromisoformat(horodatage)
    except (TypeError, ValueError):
        return None
    return (datetime.now() - ref).total_seconds() / 3600


def synchroniser(jours: int = 365, silencieux: bool = False) -> None:
    newest = date.today()
    oldest = newest - timedelta(days=jours)
    meta = {
        "recupere_a": datetime.now().isoformat(timespec="seconds"),
        "oldest": oldest.isoformat(),
        "newest": newest.isoformat(),
    }

    def dire(msg):
        if not silencieux:
            print(msg)

    client = IcuClient()

    activites = client.activities(oldest, newest)
    dump("activities", activites, meta)
    dire(f"activites : {len(activites)} sur {jours} jours")

    wellness = client.wellness(oldest, newest)
    dump("wellness", wellness, meta)
    renseignes = sum(1 for w in wellness if w.get("hrv") is not None)
    dire(f"wellness  : {len(wellness)} jours, dont {renseignes} avec HRV")

    courbe = client.power_curve(jours)
    if courbe is not None:
        dump("power_curve", courbe, meta)
        dire("courbe de puissance : recuperee")
    else:
        dire("courbe de puissance : endpoint introuvable")

    velo = [a for a in activites if a.get("type") in ("Ride", "VirtualRide")]
    if activites and len(velo) < 20:
        dire(
            "\nAttention : tres peu d'activites velo. Si ton calendrier Intervals "
            "en montre davantage, elles viennent de Strava et ne sont pas exposees "
            "par l'API. Reimporte depuis Garmin."
        )


def assurer(jours: int = 365, max_age_h: float = 12) -> None:
    """Synchronise seulement si le cache est absent ou perime.

    Appele par les scripts de calcul pour qu'on ne puisse pas produire un bilan
    sur des donnees de la semaine derniere.
    """
    age = age_cache_heures()
    if age is None:
        print("cache absent, synchronisation...")
    elif age > max_age_h:
        print(f"cache vieux de {age:.0f} h, synchronisation...")
    else:
        return
    synchroniser(jours, silencieux=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jours", type=int, default=365)
    args = parser.parse_args()
    synchroniser(args.jours)

if __name__ == "__main__":
    main()
