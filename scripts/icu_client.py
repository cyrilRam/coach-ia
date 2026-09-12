"""Client minimal pour l'API Intervals.icu.

Auth : basic auth, nom d'utilisateur litteral "API_KEY", mot de passe = la cle.
Toute la couche reseau est ici. Les autres scripts n'appellent jamais requests
directement — c'est le futur IntervalsService cote C#.
"""

from __future__ import annotations

import os
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://intervals.icu/api/v1"

load_dotenv(ROOT / ".env")


class IcuError(RuntimeError):
    pass


class IcuClient:
    def __init__(self, athlete_id: str | None = None, api_key: str | None = None):
        self.athlete_id = athlete_id or os.environ.get("ICU_ATHLETE_ID", "")
        api_key = api_key or os.environ.get("ICU_API_KEY", "")
        if not self.athlete_id or not api_key:
            raise IcuError(
                "ICU_ATHLETE_ID et ICU_API_KEY doivent etre definis dans .env "
                "(voir .env.example)."
            )
        self.session = requests.Session()
        self.session.auth = ("API_KEY", api_key)
        self.session.headers.update({"Accept": "application/json"})

    # -- couche transport -------------------------------------------------

    def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{BASE_URL}{path}"
        for attempt in range(3):
            resp = self.session.request(method, url, timeout=60, **kwargs)
            if resp.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            if resp.status_code >= 400:
                raise IcuError(f"{method} {path} -> {resp.status_code} {resp.text[:300]}")
            if not resp.content:
                return None
            return resp.json()
        raise IcuError(f"{method} {path} : rate limit persistant")

    def get(self, path: str, params: dict | None = None) -> Any:
        return self._request("GET", path, params=params)

    def post(self, path: str, payload: dict) -> Any:
        return self._request("POST", path, json=payload)

    # -- lecture ----------------------------------------------------------

    def athlete(self) -> dict:
        return self.get(f"/athlete/{self.athlete_id}")

    def activities(self, oldest: date, newest: date) -> list[dict]:
        """Activites terminees sur une plage.

        Attention : les activites arrivees via Strava ne sont PAS exposees par
        l'API (restriction des conditions Strava de novembre 2024). Si le compte
        est bas par rapport au calendrier, reimporter depuis Garmin.
        """
        return self.get(
            f"/athlete/{self.athlete_id}/activities",
            {"oldest": oldest.isoformat(), "newest": newest.isoformat()},
        ) or []

    def wellness(self, oldest: date, newest: date) -> list[dict]:
        """Un enregistrement par jour. L'id EST la date (AAAA-MM-JJ).

        Contient aussi les valeurs calculees par Intervals : ctl, atl,
        rampRate, ctlLoad, atlLoad, sportInfo.
        """
        return self.get(
            f"/athlete/{self.athlete_id}/wellness",
            {"oldest": oldest.isoformat(), "newest": newest.isoformat()},
        ) or []

    def power_curve(self, days: int = 365, sport: str = "Ride") -> dict | None:
        """Courbe de puissance record sur une fenetre.

        Renvoie un dict {"list": [{"id": "1y", "secs": [...], "watts": [...]}]}.
        Ce sont de VRAIS records, pas un modele.
        """
        newest = date.today()
        oldest = newest - timedelta(days=days)
        try:
            return self.get(
                f"/athlete/{self.athlete_id}/power-curves",
                {
                    "type": sport,
                    "oldest": oldest.isoformat(),
                    "newest": newest.isoformat(),
                },
            )
        except IcuError:
            return None

    def events(self, oldest: date, newest: date) -> list[dict]:
        """Seances planifiees et evenements du calendrier."""
        return self.get(
            f"/athlete/{self.athlete_id}/events",
            {"oldest": oldest.isoformat(), "newest": newest.isoformat()},
        ) or []

    # -- ecriture ---------------------------------------------------------

    def create_event(self, payload: dict) -> dict:
        """Cree une seance planifiee. Appele uniquement par push_block.py."""
        return self.post(f"/athlete/{self.athlete_id}/events", payload)


if __name__ == "__main__":
    client = IcuClient()
    info = client.athlete()
    print(info)
    print(f"Connecte : {info.get('name')} ({client.athlete_id})")
    print(f"FTP cote Intervals : {info.get('icu_ftp')} W")
    print("Rappel : le FTP de reference est celui de athlete.yaml, pas celui-ci.")
