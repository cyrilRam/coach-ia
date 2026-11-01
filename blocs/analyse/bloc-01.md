# Bilan & Analyse : Bloc 01 — Reprise & Capacité Aérobie
*Période du 05/10/2026 au 25/10/2026 (3 semaines, W41-W43) | Validé le 26/10/2026*

### 1. Métriques Clés & Compliance

* **Compliance globale :** 19 / 20 séances réalisées (95 %). Seule séance manquée : VT du 07/10 (pluie). Renfo du 12/10 écourté (17' pour 45'). Renfo S3 du mardi 20/10 avancé au lundi 19/10 (47').
  * `review.py` affiche 18/20 et des écarts de +300 à +400 % sur le renfo : le script additionne toutes les activités d'un même jour (vélo midi + renfo du soir). Compliance recomptée séance par séance.
* **Hors plan :** VT du mercredi 21/10 (2h07, 92 TSS) alors que la consigne était de ne pas en rajouter, vérif mécanique du 16/10 (29', 15 TSS).
* **Volume vélo + trail réalisé :** 33h39 pour 32h30 prescrites (+3 %), plus 5h05 de renfo.

| Semaine | Prescrit | Réalisé | TSS | CTL fin | TSB fin | FC repos | VFC | Sommeil (score) |
|---|---|---|---|---|---|---|---|---|
| W41 (S1) | 10h35 | 8h50 | 472 | 61.8 | -3.0 | 53.3 | 55.3 | 8.3h (81) |
| W42 (S2) | 12h05 | 13h20 | 569 | 64.8 | -16.3 | 51.1 | 62.3 | 7.9h (80) |
| W43 (S3) | 9h50 | 11h29 | 566 | 67.2 | -19.7 | 51.3 | 61.1 | 7.7h (76) |

* Les en-têtes de semaine de `bloc-01.yaml` étaient faux (S1 « ~9h15 » pour 10h35 de séances, S2 « ~10h15 » pour 12h05). Les totaux du bloc 2 seront calculés depuis les séances.
* **Charge totale :** 1607 TSS. Ramp Rate moyen ~2.1/semaine, maximum 3.0 (plafond 7). TSB jamais sous -20.
* **Évolution physiologique :** CTL 60.8 → 67.2 (+6.4), encore sous le niveau pré-coupure (72.7 en W38). FC repos 54.0 → 51.3 bpm, plus bas historique à 48 le 24/10. VFC 51.6 → 61.1 ms.

### 2. Analyse des Séances Clés

**Sorties longues du samedi — le marqueur du bloc**

| Date | Durée | D+ | NP | FC moy. | EF | Découplage |
|---|---|---|---|---|---|---|
| 10/10 | 3h25 | 1742 m | 213 W | 159 | 1.34 | 8 % |
| 17/10 | 4h48 | 2000 m | 215 W | 154 | 1.40 | 13 % |
| 24/10 | 4h57 | 2885 m | 219 W | 151 | 1.45 | -1.5 % |

* +8 % d'efficacité aérobie en 2 semaines : plus de watts pour 8 bpm de moins, sur une durée et un dénivelé croissants. Découplage négatif sur 5h et 26 m D+/km : l'objectif central du bloc est atteint.
* Le 17/10 a dépassé de 49' la durée prescrite (découverte de routes), sans coût sur la récupération.
* Sprints alactiques faits chaque semaine (jusqu'à 687 W sur 10 s le 24/10). Recrutement neuromusculaire entretenu.

**Pause déj du jeudi :** EF 1.35 (08/10) → 1.41 (15/10) → 1.45 (22/10). 2x10' tempo de la S3 conformes.

**Trails du dimanche**

| Date | Durée | D+ | GAP | FC moy. | Z4-Z5 FC |
|---|---|---|---|---|---|
| 11/10 | 1h27 | 509 m | 5'49/km | 175 | 69 % |
| 25/10 | 1h16 | 447 m | 5'41/km | 162 | 22 % |

* Gain aérobie spectaculaire : plus rapide pour -13 bpm.
* Prescription d'intensité ratée 2 fois sur 2 : séance prescrite en Z2 (FC < 164), réalisée avec 53 % (25/10) à 83 % (11/10) du temps en Z3-Z5.

**Vélotaf :** 5 A/R sur 6 prévus (W41-W42), 98 % en Z1-Z2 en W42. Le VT ajouté du 21/10, après une nuit de 6h, est monté à FC moy. 150 contre 142-144 sur le même trajet.

**Renforcement :** 5.5 séances sur 6. Renfo du jeudi jugé trop facile en S1, durci dès la S2 (54' au lieu de 30').

### 3. Ressenti Athlète & Signaux Physiologiques

* **Ressenti :** motivation maximale tout le bloc, jambes « au-delà des attentes » en S3, trail « beaucoup plus facile ». Cohérent avec l'EF, le découplage et la FC repos : aucune « illusion du tout va bien ».
* **Fausse alerte écartée :** coup de froid suspecté le 07/10 avec fatigue ressentie du jeudi au samedi en W41, sans aucune suite. FC repos et VFC se sont améliorées dès le 08/10.
* **Polarisation (temps FC, vélo + trail) :** 81 % en Z1-Z2, 12 % en Z3, 6 % en Z4+ sur le bloc. W41 60 % (reprise + trail), W42 92 %, W43 85 %.
* **Zone grise rampante côté puissance :** temps en Z3 de 58' → 89' → 109' par semaine, alors que la Z3 cardiaque baisse. Elle vient des montées passées à 236-243 W (76-78 % FTP), au-dessus du plafond de 232 W. Coût interne faible aujourd'hui, mais à contenir dès que le jeudi devient une vraie séance de force en Z3.
* **Sommeil — tendance à surveiller :** 8.3h → 7.9h → 7.7h et score moyen 81 → 80 → 76. Dégradation lente, d'origine professionnelle (réveil très tôt le 20/10, mise en prod jusqu'à 00h30 le 21/10), pas liée à la charge. Elle reste sans effet sur la FC repos ou la VFC, mais c'est le premier indicateur qui bouge.
* **Aucun signal d'alerte :** pas de hausse de la FC repos, pas de chute de la VFC, pas de dérive cardiaque anormale.

### 4. Bilan des Acquis & Décisions pour le Bloc Suivant

**Acquis**
* Base aérobie reconstruite : EF +8 %, découplage maîtrisé sur 5h de montagne, FC repos et VFC au meilleur niveau mesuré.
* Tolérance au volume validée : 13h20 en S2 absorbées avec les meilleurs marqueurs de santé du bloc.
* Routine renfo installée (2 séances par semaine tenues).

**À consolider**
* L'intensité du trail : 2 trails sur 2 au-dessus de la prescription.
* La discipline du plafond en col le samedi.
* Le sommeil, qui s'érode semaine après semaine.

**Ajustements pour le bloc 02 (Force sous-max & Couple)**
1. **Volume :** progression 12h → 13h → 13h30 → 10h d'assimilation maintenue, comme dans `saison-2026-2027.yaml`. Totaux de semaine calculés à partir des séances.
2. **Garde-fou sommeil :** premier déclencheur du bloc. Moyenne hebdo sous 7.3h, ou deux nuits sous 6h30 avec un score inférieur à 70 → on supprime la séance de force du jeudi suivant. Si cela se reproduit en S2 ou S3, l'assimilation est avancée. Nuit de moins de 6h30 → VT du lendemain en Z1 pure (FC < 148).
3. **Nouvelles références santé :** FC repos 51 bpm (alerte à plus de 56-57 bpm durablement), VFC ~61 ms (alerte sous 50 ms).
4. **Trail :** alerte FC à 160 bpm sur la Fenix, marcher dès qu'elle sonne. Si le trail dérive encore en S1-S2, il est compté comme une des 3 séances dures de la semaine.
5. **Samedi :** plafond de 232 W maintenu dans les cols. La Z3 se fait le jeudi (force basse cadence), le couple se travaille en départs arrêtés.
6. **Renfo :** passage de la PPG au poids de corps à de la force avec charge, en cohérence avec le thème du bloc. Cyril demande plus de difficulté.
7. **Assimilation :** 3 semaines de charge sans assimilation à l'entrée du bloc 2. La S4 d'assimilation n'est pas négociable : 6 semaines de charge consécutives au total.
