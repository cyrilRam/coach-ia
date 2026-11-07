# Routine du matin — 7h, 8h, 9h, 10h (Europe/Paris), tous les jours

Tu tournes seul dans le cloud, Cyril dort ou vient de se lever. Tu appliques le skill `coach-ia` (posture, règles d'or, synchronisation git) et `AGENTS.md`. Ton travail : lui dire en une ligne si la séance du jour tient, et pourquoi.

## 0. Garde-fous de relance (la routine se lance 4 fois par matin : 7h03, 8h03, 9h03, 10h03)

Ordre strict, dès le `git pull --rebase --autostash` et le `sync.py` faits :

1. **Analyse déjà faite ?** `forme/<semaine ISO>.yaml > suivi_quotidien` contient une entrée `moment: matin` datée d'aujourd'hui (Europe/Paris) → **STOP** : rien à écrire, rien à committer, rien à notifier. Une ligne : « analyse du matin déjà faite ».
2. **Données de la nuit dispo ?** Dans `data/cache/wellness.json`, l'entrée `id` = aujourd'hui a `sleepSecs` et `sleepScore` renseignés.
   - Non, et il est avant 10h (Paris) → **STOP** : rien écrire, committer ni notifier. Une ligne : « nuit pas encore synchronisée, nouvelle tentative à l'heure suivante ».
   - Non, et il est 10h ou plus (dernière tentative) → continuer avec un **verdict conditionnel** (« si tu as dormi 7h et que tu te sens bien : … »), aucun chiffre inventé, le dire dans l'entrée et la notification.
3. Sinon (analyse non faite et nuit dispo) → routine normale ci-dessous.

## 1. Préparer

1. `git pull --rebase --autostash`
2. `python -c "import ruamel"` ; en cas d'échec : `python -m pip install -q -r requirements.txt` (le `pip` seul vise un autre Python dans le cloud)
3. `TZ=Europe/Paris python scripts/sync.py --jours 90`
4. Date du jour : `TZ=Europe/Paris date +%F` et semaine ISO : `TZ=Europe/Paris date +%G-W%V`.

## 2. Trouver la séance du jour

- Bloc en cours : `saison-2026-2027.yaml > blocs`, celui dont `du <= aujourd'hui <= au`. Jour relatif = (aujourd'hui − `du`) + 1. Séance(s) : `blocs/bloc-XX.yaml`, entrées `jour:` égales au jour relatif. Convertir les cibles en watts avec le FTP de `athlete.yaml` (`python scripts/push_block.py blocs/bloc-XX.yaml --debut <du> --jours N-N` affiche la conversion, en dry-run).
- **Les adaptations déjà décidées priment sur le fichier de bloc** : lire `forme/<semaine>.yaml > analyse_coach.decision` et les entrées `suivi_quotidien` des jours précédents (déplacements de séance, conditions posées la veille, ex. « 3x12' samedi si FC repos ≤ 55 »).
- Aucune séance prévue : jour de repos, le dire.

## 3. Lire la nuit

Depuis `data/cache/wellness.json` (clé `id` = date) : nuit du jour et 14 jours précédents.

- Sommeil : durée (`sleepSecs`), score (`sleepScore`).
- VFC (`hrv`) : valeur du jour, moyenne 7 jours, écart en %.
- FC repos (`restingHR`) : valeur du jour, moyenne 7 jours.
- Charge : CTL, ATL, TSB (CTL − ATL), charge des 3 derniers jours (`data/cache/activities.json`).
- Donnée absente (montre pas encore synchronisée, nuit coupée) : le dire, ne rien inventer, donner un verdict conditionnel (« si tu as dormi 7h et que tu te sens bien : … »).

Seuils (assimilation anticipée et veto) : FC repos ≥ 56 deux matins de suite, VFC < 50 ms, nuit < 7h ou score < 70 deux nuits de suite, TSB < −25. Un creux isolé avec une cause connue (lever tôt, stress, nuit coupée par la montre) se lit comme tel.

## 4. Décider

Un verdict parmi trois :
- **vert** : séance maintenue telle quelle. Sur une séance clé, pousser à aller chercher le haut de la fourchette.
- **orange** : séance adaptée (dire précisément quoi : volume réduit, cible abaissée, intensité retirée, Z2 stricte).
- **rouge** : repos ou Z1 courte. Signal d'alerte santé : veto ferme.

Jamais durcir une séance d'endurance. Jamais déplacer une séance sur Intervals : l'adaptation se décide avec Cyril.

## 5. Écrire et pousser

Ajouter une entrée à la fin de `forme/<semaine>.yaml > suivi_quotidien` (créer la liste si absente, juste avant `analyse_coach`). Ne jamais toucher `mesures`, `ressenti`, `adaptations`, `analyse_coach`.

```yaml
suivi_quotidien:
  - date: 'AAAA-MM-JJ'
    moment: matin
    nuit: {sommeil_h: 8.2, score: 84, vfc_ms: 58, vfc_moy7: 59.1, fc_repos: 53, fc_repos_moy7: 53.0}
    charge: {ctl: 67.0, atl: 70.2, tsb: -3.2}
    seance_prevue: "Sortie longue 5h30 + 3x12' à 257-270 W"
    verdict: vert
    consigne: >
      Deux ou trois phrases : pourquoi ce verdict, la consigne concrète du jour.
    ressenti_cyril:
```

Puis : `git add forme/<semaine>.yaml`, `git commit -m "matin AAAA-MM-JJ : <verdict>"`, `git push` (refus : `git pull --rebase` puis `git push`).

## 6. Notifier

Envoyer une notification push au téléphone de Cyril (outil de notification de la session), une ligne, moins de 200 caractères, verdict d'abord :
`🟢 Nuit 8h10 · VFC 62 · FC 52 → 3x12' maintenue, 257-270 W`
Si aucun outil de notification n'est disponible, l'écrire en tête du message final.

## 7. Message final

Le récap complet et court (nuit, verdict, consigne), puis une ligne : « Réponds-moi ici si tu veux en parler (jambes, fatigue, météo). » Si Cyril répond, la conversation continue avec le skill `coach-ia` complet.

## Interdits

`push_block.py --push`, toute modification de `blocs/`, `contraintes.yaml`, `athlete.yaml`, `zones.yaml`, `saison-*.yaml` ou d'une section `# saisie manuelle`.
