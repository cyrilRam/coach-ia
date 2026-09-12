# Dossier Analyses de Blocs (Reviews)

Ce dossier contient les bilans et analyses approfondies rédigés par le coach à la fin de chaque bloc d'entraînement (Rituel 5 du coaching).

## Rôle et Utilisation

À la fin de chaque bloc (ex: après les 4 semaines du Bloc 1) :
1. Le script `python scripts/review.py blocs/bloc-XX.yaml --debut AAAA-MM-JJ` est exécuté pour mesurer la compliance et les métriques réelles.
2. Le coach analyse les fichiers de forme hebdomadaire (`forme/AAAA-Wxx.yaml`), les ressentis de Cyril et la réponse physiologique.
3. Un fichier `blocs/analyse/bloc-XX.md` est rédigé et conservé ici pour ancrer l'apprentissage et orienter la prescription du bloc suivant.

## Structure type d'une analyse (`bloc-XX.md`)

```markdown
# Bilan & Analyse : Bloc XX — [Nom du bloc]
*Période du [Date début] au [Date fin] | Validé le [Date]*

### 1. Métriques Clés & Compliance
* **Compliance globale :** X / Y séances réalisées (X %)
* **Volume total réalisé :** X heures (prévu : Y h)
* **Charge totale (TSS) :** X TSS (prévu : Y TSS)
* **Évolution physiologique :** CTL début -> fin (+X), TSB final, FC repos moyenne

### 2. Analyse des Séances Clés
* Sorties longues du week-end (gestion de l'allure, tolérance musculaire, nutrition).
* Séances d'intensité / Sprints (qualité neuromusculaire, watts atteints).
* Régularité du vélotaf et du renforcement musculaire.

### 3. Ressenti Athlète & Signaux Physiologiques
* Analyse des ressentis hebdomadaires (jambes, sommeil, motivation).
* Détection d'éventuels signes de fatigue aiguë ou de dérive.

### 4. Bilan des Acquis & Décisions pour le Bloc Suivant
* Ce qui est validé et acquis.
* Ce qui doit être consolidé.
* Ajustements à intégrer dans le bloc suivant.
```
