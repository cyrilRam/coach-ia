# Coach IA — Guide d'utilisation

Système de coaching cycliste personnel : des fichiers YAML locaux comme source de vérité, des scripts Python pour communiquer avec Intervals.icu, et ton agent IA comme coach et sparring-partner d'entraînement.

Ici, pas d'interface web superflue : **tout se pilote en conversation avec le coach et via des scripts simples et déterministes**.

---

## Sommaire

1. [Installation rapide](#1-installation-rapide)
2. [Construire sa saison (Le Macrocycle)](#2-construire-sa-saison-le-macrocycle)
3. [Gérer un bloc d'entraînement au quotidien](#3-gérer-un-bloc-dentraînement-au-quotidien)
4. [Analyses et Mémoire du Coaching (Hebdo & Blocs)](#4-analyses-et-mémoire-du-coaching-hebdo--blocs)
5. [Gérer les imprévus (Maladie, voyages, fatigue)](#5-gérer-les-imprévus-maladie-voyages-fatigue)
6. [Stratégie de course à J-7](#6-stratégie-de-course-à-j-7)
7. [Aide-mémoire des commandes](#7-aide-mémoire-des-commandes)
8. [Les règles d'or du système](#8-les-règles-dor-du-système)

---

## 1. Installation rapide

```bash
# 1. Environnement Python
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Clés Intervals.icu (Settings > Developer Settings)
cp .env.example .env
# Renseigne ICU_API_KEY et ICU_ATHLETE_ID (dans l'URL intervals.icu/athlete/iXXXXXX)

# 3. Vérifier la connexion
python scripts/icu_client.py
```

---

## 2. Construire sa saison (Le Macrocycle)

La planification de la saison s'effectue en amont de l'année sportive au cours d'une session de cadrage avec le coach.  
Pour la saison en cours, voir la synthèse complète dans [PLAN_SAISON_2026_2027.md](PLAN_SAISON_2026_2027.md) et la configuration dans [saison-2026-2027.yaml](saison-2026-2027.yaml).

### Étape 1 : Rafraîchir son profil physiologique
```bash
python scripts/sync.py --jours 365
python scripts/build_profile.py
```
Met à jour [athlete.yaml](athlete.yaml) (records réels, W/kg, volume moyen, modèle CP/W').

### Étape 2 : Cadrer les objectifs et les règles
- **Objectif majeur (A) :** ex. **MERCAN’TOUR BONETTE** (13 juin 2027 — 177 km, 4 800 m D+).
- **Objectifs secondaires (B) :** Paris-Nice Challenge, Madone-Peille, GFNY Cannes.
- **Courses de préparation :** Lazardières Cannes, La Vençoise.
- **Enveloppe de volume :** Entre **8h et 15h** par semaine, sorties en semaine plafonnées à **2h max sur pause déj**.
- **Protocole de tests de terrain :** Protocole **3 min + 12 min en côte** (début janvier pour calibrer le Sweet Spot/Seuil et mi-février avant Paris-Nice), évitant le test 20 min classique.
- **Règles d'affûtage et de récupération :**
  - **Semaine pré-course :** volume réduit de 40 à 50% avec piqûres d'intensité courtes pour viser un TSB positif (+5 à +15).
  - **Semaine post-course :** régénération active en Z1/Z2 sans travail dur (avec amorce rapide de la PMA en fin de semaine post-Paris-Nice pour enchaîner sur la Madone-Peille).

### Étape 3 : Figer l'architecture des 9 blocs
Le macrocycle est découpé en 4 grandes phases :
1. **Fondations Hivernales & Force (Octobre – Décembre) :** Blocs 1 à 3 (reprise aérobie, force basse cadence 50-60 rpm, sprints courts alactiques le week-end, sweet spot base).
2. **Seuil & Montagne (Janvier – Mi-Mars) :** Blocs 4 à 6 (sweet spot long, seuil Z4, over-unders, affûtage Paris-Nice).
3. **PMA & Rythme Punchy (Mi-Mars – Début Mai) :** Blocs 7 et 8 (déblocage PMA Z5, Madone-Peille, GFNY Cannes, Lazardières, Vençoise).
4. **Haute Montagne & Bonette (Mai – Juin) :** Bloc 9 (sorties reines 6h, 4 000 m D+, affûtage sur 2 semaines vers le 13 juin).

---

## 3. Gérer un bloc d'entraînement au quotidien

### 1. Prescription du bloc (`blocs/bloc-XX.yaml`)
Le coach rédige le bloc en jours relatifs (`jour: 1`, `jour: 2`...) et en pourcentages du FTP déclaré :
* **Sorties longues du samedi :** progression de 3h30 à 5h-6h dans les cols de l'arrière-pays niçois.
* **Sprints qualitatifs :** placés sur les sorties du week-end (samedi et dimanche) sur routes ouvertes sécurisées (6 à 10 sprints de 10-15s alactiques et départs arrêtés à fort couple).
* **Vélotaf (Mardi & Mercredi) :** 100% Z2 fondamentale souple (55 km / 2h10), zéro sprint pour préserver la sécurité et la qualité.
* **Renforcement musculaire structuré :** 2 séances par semaine intégrées avec détail complet des exercices, séries, répétitions, tempo et récupération (PPG le lundi sur jour off, posture/gainage le jeudi après vélo).

### 2. Simulation (Dry-Run) et Push vers Intervals.icu
```bash
# 1. Simulation obligatoire : affiche les dates réelles et les watts convertis
python scripts/push_block.py blocs/bloc-01.yaml --debut 2026-10-05

# 2. Push réel vers Intervals.icu (uniquement après ton accord explicite)
python scripts/push_block.py blocs/bloc-01.yaml --debut 2026-10-05 --push
```
Le script injecte automatiquement les paliers d'intervalles (avec syntaxe de répétition `6x`, `8x` isolée par des sauts de ligne) et les fiches complètes de renforcement musculaire.

### 3. Méthode pour concevoir les blocs suivants (Boucle d'apprentissage)
Avant de rédiger le bloc suivant ($N+1$), le coach ne repart jamais d'une feuille blanche. Il applique un protocole d'analyse rigoureux :
1. **Analyser en détail le bilan du bloc précédent :** Lecture obligatoire de [`blocs/analyse/bloc-[N-1].md`](blocs/analyse/) pour évaluer la compliance (% séances faites), la charge réelle vs prévue, les séances sautées et les décisions actées.
2. **Analyser en détail les comptes-rendus des semaines précédentes :** Examen des fichiers [`forme/AAAA-Wxx.yaml`](forme/) du bloc écoulé. Le coach croise les métriques (CTL, ATL, TSB, dérive FC repos) avec tes **scores de santé et ressentis réels** (sommeil, niveau de fatigue, jambes, motivation) et les diagnostics `analyse_coach`.
3. **Ajuster sur-mesure la prescription suivante :** Les durées, la charge et la progression des thèmes (ex: passage au travail de force en côte au Bloc 2) sont calibrées en fonction de ce qui a réellement été assimilé sur le terrain. **Règle absolue :** si le sommeil ou la récupération globale sont dégradés, le bloc suivant n'augmente jamais la charge et intègre des allègements préventifs.

---

## 4. Analyses et Mémoire du Coaching (Hebdo & Blocs)

Le système conserve une mémoire qualitative à deux niveaux :

### A. Suivi Hebdomadaire (`forme/AAAA-Wxx.yaml`)
Chaque dimanche soir :
1. **Rapatrier les mesures :**
   ```bash
   python scripts/weekly.py
   ```
2. **Saisie de tes ressentis :** Renseigne la section `# saisie manuelle` (`jambes`, `sommeil`, `motivation`, `imprevus`). Ce retour qualitatif et tes indicateurs de santé (qualité du sommeil, fatigue résiduelle) constituent les signaux les plus importants du système.
3. **Diagnostic du coach (`analyse_coach`) :** Le coach analyse le croisement santé / charge / ressenti et consigne son analyse directement dans le fichier :
   ```yaml
   analyse_coach:
     maj: '2026-09-12'
     synthese: Analyse physiologique de la semaine, réponse cardiovasculaire, dérive de FC.
     decision: Recommandations et ajustements pour la semaine suivante.
   ```

### B. Bilan de fin de bloc (`blocs/analyse/bloc-XX.md`)
À la fin de chaque bloc de 3 à 5 semaines :
1. **Lancer la revue :**
   ```bash
   python scripts/review.py blocs/bloc-01.yaml --debut 2026-10-05
   ```
2. **Débriefing & Rédaction :** Le coach débriefe avec toi la compliance (% réalisé), la charge réelle vs cible et les acquis, puis enregistre un rapport structuré dans le dossier [`blocs/analyse/`](blocs/analyse/bloc-01.md). Ce document sert de base pour calibrer le bloc suivant.

---

## 5. Gérer les imprévus (Maladie, voyages, fatigue)

Règle d'or : **On ne rattrape JAMAIS des séances manquées en surchargeant les jours suivants.**

### Que dire au coach ?
* **Maladie :** *"Fièvre depuis mardi, pas de vélo avant vendredi. Comment on adapte ?"*
* **Déplacement :** *"À Paris du 23 au 28 sans vélo. On cale une coupure ?"*
* **Fatigue / TSB très bas :** *"Sommeil dégradé et jambes en bois. On allège la séance de seuil ?"*

### Comment le coach réagit :
1. Priorisation de la santé et de la fraîcheur (allègement, repos ou Z1/Z2 souple).
2. Réajustement du fichier `blocs/bloc-XX.yaml`.
3. Suppression des séances obsolètes sur Intervals.icu et re-push du calendrier adapté.

---

## 6. Stratégie de course à J-7

7 jours avant chaque course (`saison-2026-2027.yaml`) :
1. Analyse du parcours (profil altimétrique, pourcentages des cols, météo).
2. Évaluation de l'état de fraîcheur (TSB cible entre +5 et +15, W/kg).
3. Plan d'allure personnalisé : watts cibles par col (modèle CP/W'), stratégie de braquet et plan de ravitaillement glucidique (60 à 90 g/h).

---

## 7. Aide-mémoire des commandes

| Commande | Rôle | Quand l'exécuter ? |
|---|---|---|
| `python scripts/sync.py` | Télécharge activités & wellness dans `data/cache/` | Avant tout calcul de profil ou bilan |
| `python scripts/build_profile.py` | Met à jour records et modèle CP/W' dans `athlete.yaml` | 1 fois par mois ou après un bloc |
| `python scripts/weekly.py` | Génère la section `mesures` dans `forme/AAAA-Wxx.yaml` | Chaque dimanche soir |
| `python scripts/push_block.py <bloc> --debut <date>` | Prévisualise séances, watts et intervalles (dry-run) | Avant d'envoyer un bloc |
| `python scripts/push_block.py <bloc> --debut <date> --push` | Envoie réellement les séances sur Intervals.icu | Après validation explicite |
| `python scripts/review.py <bloc> --debut <date>` | Compare prévu vs réalisé sur un bloc terminé | À la fin d'un bloc de 3-5 semaines |

---

## 8. Les règles d'or du système

1. **Le FTP est déclaré, jamais calculé :** `athlete.yaml > seuils.ftp` ne change qu'après un test terrain validé par toi.
2. **Rien n'est poussé sur Intervals sans validation explicite :** `push_block.py` tourne en `--dry-run` par défaut.
3. **Tu es propriétaire de tes ressentis :** Les sections `# saisie manuelle` ne sont jamais modifiées par l'agent.
4. **[contraintes.yaml](contraintes.yaml) est inviolable :** Repos lundi/vendredi, vélotaf mardi/mercredi, max 2h pause déj en semaine, sortie longue samedi et trail dimanche bornent toute planification.
5. **Mémoire qualitative vivante :** Les synthèses hebdos sont consignées dans `forme/` et les bilans de blocs sont archivés dans `blocs/analyse/`.
6. **Priorité absolue aux scores de santé et à la fatigue ressentie :** Pour toute analyse et toute planification, le sommeil, les signaux cardiovasculaires (FC repos) et le ressenti subjectif de fatigue prévalent sur les modèles mathématiques (TSS, CTL, TSB). Si le sommeil est perturbé ou la fatigue prononcée, la charge s'allège immédiatement.
7. **Canalisateur d'intensité (« Frapper fort au bon moment, assimiler impérativement après ») :** Cyril a besoin de « se faire mal » pour progresser. Le coach n'est pas frileux sur les blocs de charge et les séances cibles (semaines chocs de cols, Seuil, PMA) où l'exigence est maximale. En revanche, le coach est intraitable sur la stricte facilité des séances d'endurance (Z2/vélotaf), impose la décharge post-choc, et déclenche un veto absolu si des signaux inquiétants apparaissent (score de sommeil faible, forte dérive cardiaque) afin de désamorcer une infection en incubation avant que l'illusion du « tout va bien » ne cloue l'athlète au lit.
