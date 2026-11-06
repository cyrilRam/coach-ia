# Routine du soir — 21h (Europe/Paris), tous les jours

Tu tournes seul dans le cloud. Tu appliques le skill `coach-ia` (posture, règles d'or, synchronisation git) et `AGENTS.md`. Ton travail : faire le point sur la journée et préparer demain.

## 1. Préparer

Comme la routine du matin (`routines/matin.md`, étape 1) : pull, dépendances, `TZ=Europe/Paris python scripts/sync.py --jours 90`, date et semaine ISO du jour.

## 2. Comparer le réalisé au prévu

- Prévu : séance(s) du jour selon `routines/matin.md` étape 2, plus la consigne du matin (`suivi_quotidien`, entrée `matin` du jour).
- Réalisé : activités du jour dans `data/cache/activities.json` (`start_date_local`) : durée, TSS, NP, FC moyenne et max, D+, temps par zone (`icu_zone_times`, `icu_hr_zone_times`), découplage (`decoupling`), EF.
- Juger : cibles tenues sur les intervalles, plafond Z2 respecté hors blocs (zone grise interdite), découplage anormal en Z2 (> 10 %), FC haute pour la puissance. Une séance sautée ou remplacée : le constater, sans rattrapage.
- Vélotaf : pas de capteur de puissance, lecture à la FC.

## 3. Situer la charge

CTL, ATL, TSB du soir ; heures de la semaine réalisées contre prévues ; respect de la limite de +30 % de volume par rapport à la semaine précédente (`contraintes.yaml`).

## 4. Préparer demain

Séance(s) de demain (même méthode), avec les cibles en watts, et deux ou trois points d'attention : heure de coucher, nutrition pour une sortie longue, équipement si froid ou pluie (météo de Nice si la recherche web est disponible), condition du matin à vérifier.

Le dimanche : lancer aussi `TZ=Europe/Paris python scripts/weekly.py --semaine <semaine courante>` pour rafraîchir `mesures`, committer le fichier, et rappeler dans la notification que le bilan de semaine se fait en conversation.

## 5. Écrire et pousser

Ajouter une entrée à la fin de `forme/<semaine>.yaml > suivi_quotidien`. Ne jamais toucher `ressenti`, `adaptations`, `analyse_coach` (ni `mesures`, sauf via `weekly.py` le dimanche).

```yaml
  - date: 'AAAA-MM-JJ'
    moment: soir
    realise:
      - {nom: "Sortie longue", duree_min: 330, tss: 240, np_w: 216, fc_moy: 150, d_plus_m: 2800}
    charge: {ctl: 68.1, atl: 85.0, tsb: -16.9, heures_semaine: 11.4, heures_prevues: 13.0}
    ecarts: >
      Ce qui a différé de la prescription, ou « conforme ».
    demain: "Trail 1h20 Z2, alerte FC 160"
    consigne: >
      Deux ou trois phrases pour demain.
    ressenti_cyril:
```

Puis : `git add forme/<semaine>.yaml`, `git commit -m "soir AAAA-MM-JJ"`, `git push`.

## 6. Notifier

Une notification push d'une ligne, moins de 200 caractères :
`✅ 3x12' faite à 266 W, Z2 propre · Demain : trail 1h20, alerte FC 160`
Si aucun outil de notification n'est disponible, l'écrire en tête du message final.

## 7. Message final

Le récap court, puis : « Dis-moi comment tu te sens (jambes, fatigue) si tu veux, je le note. » Si Cyril répond, ses mots vont dans `ressenti_cyril` de l'entrée du soir (citation fidèle), commit et push.

## Interdits

Les mêmes que le matin : pas de `push_block.py --push`, aucune modification de `blocs/`, `contraintes.yaml`, `athlete.yaml`, `zones.yaml`, `saison-*.yaml` ou d'une section `# saisie manuelle`.
