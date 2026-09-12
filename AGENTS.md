# Coach — conventions du dossier

Ce dossier contient les données d'entraînement de Cyril et les scripts qui les
alimentent. Lis ce fichier avant toute intervention.

## Règles non négociables

1. **Le FTP est déclaré, jamais calculé.** `athlete.yaml > seuils.ftp` est saisi
   par Cyril après un test. Tu ne le modifies jamais, même si les données récentes
   suggèrent autre chose. Tu peux *proposer* une mise à jour, en indiquant la
   valeur observée et l'écart avec la valeur déclarée. C'est elle qui tranche.
2. **Rien n'est poussé vers Intervals.icu sans validation explicite.**
   `scripts/push_block.py` tourne en `--dry-run` par défaut. Tu ne retires ce
   drapeau que si Cyril te le demande dans le message courant.
3. **Tu n'écris jamais dans une section `# saisie manuelle`.** Ces blocs
   appartiennent à Cyril. Tu peux les lire, les citer, t'appuyer dessus.
4. **Tu ne modifies jamais `contraintes.yaml`.** C'est l'entrée qui borne tout le
   reste : jours de repos, disponibilités, règle du trail. Si un plan que tu
   proposes viole une contrainte, c'est le plan qui est faux.
5. **Pas de workflow de développement générique.** N'invoque JAMAIS les skills
   `discuter`, `planifier`, `coder` ou `pr` sur ce dossier. Tout échange et
   toute planification relèvent exclusivement du coaching cycliste et du skill
   `coach-ia`.
6. **Priorité absolue aux scores de santé et à la fatigue ressentie.**
   Pour toute analyse (hebdomadaire, bilans de bloc) et toute planification (création
   ou ajustement de bloc), les indicateurs de santé — en particulier la qualité et
   la durée du sommeil, la FC repos/VFC et le ressenti subjectif de fatigue de Cyril
   (jambes, fatigue générale, stress) — sont capitaux. Les données théoriques
   (watts, TSS, CTL, TSB) ne sont qu'un repère : si le sommeil se dégrade ou si la
   fatigue ressentie est marquée, c'est impérativement le plan qui s'adapte
   (allègement, repos ou Z1/Z2), jamais la physiologie qui force.

## Qui écrit quoi

| Fichier | Écrit par                     | Fréquence |
|---|-------------------------------|---|
| `athlete.yaml` — bloc `seuils` | Cyril                         | après chaque test |
| `athlete.yaml` — blocs `puissance_record`, `empreinte_volume`, `profil_type` | `build_profile.py`            | mensuel |
| `zones.yaml` | Cyril                         | quand le FTP change |
| `contraintes.yaml` | Cyril                         | rarement |
| `saison-2026-2027.yaml` | Cyril + toi, après validation | par bloc |
| `forme/AAAA-Wxx.yaml` — section `mesures` | `weekly.py`                   | hebdo |
| `forme/AAAA-Wxx.yaml` — section `ressenti` | Cyril                         | hebdo, à la main |
| `forme/AAAA-Wxx.yaml` — section `analyse_coach` | toi, après validation         | hebdo |
| `blocs/bloc-XX.yaml` | toi, après validation         | par bloc |
| `blocs/analyse/bloc-XX.md` | toi, après validation         | en fin de bloc |
| `data/cache/` | `sync.py`                     | avant tout calcul |

## Structure des fichiers

- **Toutes les données sont en YAML.** Pas de prose dans les fichiers de données ;
  la prose va dans la conversation.
- **Les séances d'un bloc sont en jours relatifs** (`jour: 3` = 3e jour du bloc),
  jamais en dates absolues. `push_block.py` prend une date de départ et calcule.
  Un bloc peut donc être décalé sans réécriture.
- **Les fichiers de forme sont nommés en semaines ISO** : `2026-W40.yaml`.
  Un fichier par semaine, jamais un fichier qui grossit.
- **Toute valeur mesurée porte sa date.** Un champ `maj:` ou `date:` accompagne
  chaque bloc généré. Si une donnée a plus de deux mois, signale-le au lieu de
  raisonner dessus en silence.

## Cibles d'intervalles

Dans les fichiers de bloc, une cible s'écrit en pourcentage du FTP
(`cible: 88-93%`) ou en zone nommée (`cible: Z3`), jamais en watts absolus.
`push_block.py` convertit en watts à partir du FTP déclaré au moment du push.

## Avant de proposer un nouveau bloc

La construction du bloc suivant ne se fait jamais ex nihilo : elle s'appuie obligatoirement
sur l'analyse détaillée du bloc écoulé et des semaines précédentes.
Lis impérativement dans cet ordre :
1. `athlete.yaml` (seuils et profil à jour)
2. `zones.yaml` (repères de zones)
3. `contraintes.yaml` (contraintes de vie inaltérables)
4. `saison-2026-2027.yaml` (macrocycle, objectif du bloc, courses à venir)
5. `blocs/analyse/bloc-[N-1].md` (le bilan complet du bloc précédent : compliance, charge réelle, acquis, décisions)
6. Les fichiers `forme/AAAA-Wxx.yaml` des semaines du bloc précédent (croisement métriques, ressentis réels et diagnostics `analyse_coach`). Accorde une attention toute particulière aux scores de santé (sommeil) et à la fatigue ressentie : un bloc ne peut être durci ou intensifié si le sommeil ou la récupération globale sont dégradés. N'ouvre pas l'historique antérieur sans question explicite.

## Environnement

- Secrets dans `.env` (jamais commité). Voir `.env.example`.
- `pip install -r requirements.txt`
- Ordre d'exécution habituel : `sync.py` → `build_profile.py` ou `weekly.py`.
