"""Calcule le profil athlete depuis le cache et met a jour athlete.yaml.

Ecrit trois blocs generes, jamais le bloc "seuils" :

  puissance_record  records REELS extraits de la courbe de puissance Intervals
  modele_cp         parametres CP / W' / p_max + points modelises
  empreinte_volume  volume, frequence, charge, ratio de denivele

Les deux premiers ne racontent pas la meme chose :
  - un record est une observation, une fenetre glissante reellement produite
  - le modele est une interpolation a partir de deux parametres ajustes

Le profil s'etablit sur les records. Le modele sert a predire la tenue sur un
effort donne (col, echappee), pas a decrire l'athlete.

    python scripts/sync.py && python scripts/build_profile.py
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

from sync import charger

ROOT = Path(__file__).resolve().parent.parent
DUREES = [("5s", 5), ("1min", 60), ("5min", 300), ("20min", 1200), ("60min", 3600)]

yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)


def parse_jour(valeur: str | None) -> date | None:
    if not valeur:
        return None
    try:
        return datetime.fromisoformat(valeur.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(valeur[:10])
        except ValueError:
            return None


# -- records reels --------------------------------------------------------

def pics_depuis_courbe(courbe, poids: float) -> tuple[list[dict], float | None]:
    """Extrait les pics aux durees cles de la courbe de puissance.

    La reponse d'Intervals est un dict {"list": [{...}]}. secs[] est indexe en
    secondes, watts[] contient le record atteint sur chaque duree.
    Renvoie aussi le poids utilise par Intervals, pour signaler un ecart.
    """
    if not courbe:
        return [], None

    entrees = courbe.get("list") if isinstance(courbe, dict) else courbe
    if not entrees:
        return [], None
    bloc = max(entrees, key=lambda e: len(e.get("secs") or []))

    secs = bloc.get("secs") or []
    watts = bloc.get("watts") or []
    if not secs or len(secs) != len(watts):
        return [], bloc.get("weight")

    index = {s: w for s, w in zip(secs, watts)}
    pics = []
    for label, cible in DUREES:
        w = index.get(cible)
        if not w:
            continue
        pics.append({
            "duree": label,
            "watts": int(round(w)),
            "w_kg": round(w / poids, 2) if poids else None,
            "source": "record_reel",
        })
    return pics, bloc.get("weight")


# -- modele CP / W' -------------------------------------------------------

def modele_cp(activites, poids: float) -> dict:
    """Parametres du modele de puissance critique, et points qu'il predit.

    P(t) = CP + W'/t, valide entre ~2 et ~20 min. En dehors de cette fenetre
    le modele derape : a 5 s il donnerait plusieurs milliers de watts, a 60 min
    il retombe sur CP par construction.
    On ne modelise donc que 5, 10 et 20 min.

    p_max est un parametre distinct (asymptote a duree nulle), pas un record
    de sprint. Conserve tel quel, jamais presente comme un pic.
    """
    def meilleur(champ):
        vals = [a.get(champ) for a in activites
                if isinstance(a.get(champ), (int, float)) and a.get(champ) > 0]
        return max(vals) if vals else None

    cp = meilleur("icu_rolling_ftp")
    w_prime = meilleur("icu_rolling_w_prime")
    p_max = meilleur("icu_rolling_p_max")

    bloc = {
        "maj": date.today().isoformat(),
        "source": "icu_rolling_* (modele ajuste par Intervals)",
        "cp_w": int(round(cp)) if cp else None,
        "w_prime_j": int(round(w_prime)) if w_prime else None,
        "p_max_w": int(round(p_max)) if p_max else None,
        "usage": "prediction d'effort (col, echappee). PAS un profil d'athlete.",
        "points_modelises": [],
    }

    if cp and w_prime:
        for label, secs in [("5min", 300), ("10min", 600), ("20min", 1200)]:
            w = cp + w_prime / secs
            bloc["points_modelises"].append({
                "duree": label,
                "watts": int(round(w)),
                "w_kg": round(w / poids, 2) if poids else None,
                "source": "modele_cp_wprime",
            })
    return bloc


# -- empreinte de volume --------------------------------------------------

def empreinte(activites) -> dict:
    semaines: dict[tuple, dict] = defaultdict(
        lambda: {"secondes": 0.0, "tss": 0.0, "n": 0, "km": 0.0, "dplus": 0.0}
    )
    for a in activites:
        jour = parse_jour(a.get("start_date_local") or a.get("start_date"))
        if not jour:
            continue
        s = semaines[jour.isocalendar()[:2]]
        s["secondes"] += a.get("moving_time") or 0
        s["tss"] += a.get("icu_training_load") or 0
        s["km"] += (a.get("distance") or 0) / 1000
        s["dplus"] += a.get("total_elevation_gain") or 0
        s["n"] += 1

    actives = [s for s in semaines.values() if s["n"] > 0]
    if not actives:
        return {}

    heures = [s["secondes"] / 3600 for s in actives]
    charges = [s["tss"] for s in actives]
    km_total = sum(s["km"] for s in actives)
    dplus_total = sum(s["dplus"] for s in actives)

    return {
        "maj": date.today().isoformat(),
        "fenetre_jours": 365,
        "heures_semaine_moyenne": round(sum(heures) / len(heures), 1),
        "heures_semaine_max": round(max(heures), 1),
        "sorties_semaine_moyenne": round(sum(s["n"] for s in actives) / len(actives), 1),
        "tss_semaine_moyenne": int(round(sum(charges) / len(charges))),
        "tss_semaine_max": int(round(max(charges))),
        "denivele_m_par_km": round(dplus_total / km_total, 1) if km_total else None,
    }


def commentaire_profil(pics: list[dict]) -> str | None:
    """Lecture brute des rapports entre records. Volontairement descriptif :
    l'interpretation revient a l'athlete, pas au script."""
    par_duree = {p["duree"]: p["watts"] for p in pics}
    if "5min" not in par_duree or "20min" not in par_duree:
        return None
    ratio = par_duree["5min"] / par_duree["20min"]
    if ratio > 1.20:
        forme = "PMA nettement au-dessus du seuil : profil plutot punchy"
    elif ratio < 1.10:
        forme = "PMA proche du seuil : profil plutot rouleur/diesel"
    else:
        forme = "rapport PMA/seuil equilibre"
    return f"{forme} (5min/20min = {ratio:.2f}). A confronter au ressenti."


# -- ecriture -------------------------------------------------------------

def main() -> None:
    chemin = ROOT / "athlete.yaml"
    with chemin.open(encoding="utf-8") as f:
        profil = yaml.load(f)

    poids = float(profil.get("identite", {}).get("poids_kg") or 0)
    activites = charger("activities")
    velo = [a for a in activites if a.get("type") in ("Ride", "VirtualRide")]

    try:
        courbe = charger("power_curve")
    except FileNotFoundError:
        courbe = None

    pics, poids_icu = pics_depuis_courbe(courbe, poids)

    profil["puissance_record"]["maj"] = date.today().isoformat()
    profil["puissance_record"]["fenetre_jours"] = 365
    profil["puissance_record"]["fiable"] = bool(pics)
    profil["puissance_record"]["pics"] = pics

    if "modele_cp" not in profil:
        profil["modele_cp"] = CommentedMap()
    profil["modele_cp"].update(modele_cp(velo, poids))

    emp = empreinte(activites)
    if emp:
        profil["empreinte_volume"].update(emp)

    profil["profil_type"]["maj"] = date.today().isoformat()
    profil["profil_type"]["commentaire"] = commentaire_profil(pics)

    with chemin.open("w", encoding="utf-8") as f:
        yaml.dump(profil, f)

    # -- rapport console --------------------------------------------------

    print(f"athlete.yaml mis a jour ({len(velo)} sorties velo)\n")

    if pics:
        print("Records reels (courbe Intervals, 365 j)")
        for p in pics:
            print(f"  {p['duree']:>6} : {p['watts']:>4} W   {p['w_kg']} W/kg")
    else:
        print("Records reels : AUCUN. La courbe n'a pas ete recuperee.")
        print("  Relance sync.py, ou releve les pics dans l'onglet Power.")

    m = profil["modele_cp"]
    if m.get("cp_w"):
        print(f"\nModele CP/W'  CP {m['cp_w']} W   W' {m['w_prime_j']} J   "
              f"p_max {m['p_max_w']} W")
        for p in m["points_modelises"]:
            print(f"  {p['duree']:>6} : {p['watts']:>4} W   {p['w_kg']} W/kg  (modelise)")

    if emp:
        print(f"\nVolume : {emp['heures_semaine_moyenne']} h/sem "
              f"(max {emp['heures_semaine_max']} h), "
              f"{emp['sorties_semaine_moyenne']} sorties/sem")

    # -- signaux ----------------------------------------------------------

    if poids_icu and poids and abs(poids_icu - poids) > 0.3:
        print(f"\nEcart de poids : {poids} kg dans athlete.yaml, {poids_icu} kg "
              f"cote Intervals. Les W/kg des deux sources ne concorderont pas "
              f"tant que ce n'est pas tranche.")

    ftp = profil["seuils"]["ftp"]["valeur_w"]
    p20 = next((p for p in pics if p["duree"] == "20min"), None)
    if p20:
        estime = int(p20["watts"] * 0.95)
        ecart = estime - ftp
        if abs(ecart) >= 10:
            print(
                f"\nInfo : ton record 20 min ({p20['watts']} W) donne un FTP estime "
                f"a {estime} W, soit {ecart:+d} W par rapport au FTP declare "
                f"({ftp} W). Le fichier n'a PAS ete modifie — a toi de decider si "
                f"un test s'impose."
            )


if __name__ == "__main__":
    main()
