# Utilisation du script de calcul des frais kilométriques
## Fonctions
Ce script offre plusieurs fonctions afin de permettre le calcul de ses frais réels :

- `add` : ajouter une journée de déplacement dans l'historique (fichier json). Cette fonction requiert les arguments :
    - `--date` : journée du déplacement (au format jj/mm/aaaa)
    - `--distance` : distance totale parcourue ce jour (nombre décimal)
- `calculate` : calculer pour une année donnée le montant des frais réels à déclarer selon le [barème](https://www.service-public.fr/particuliers/actualites/A14686) du gouvernement. Cette fonction requiert les arguments :
    - `--year` : année pour laquelle effectuer le calcul (au format aaaa)
    - `--power` : puissance fiscale du véhicule (liste de choix [3, 4, 5, 6, 7])

Il est nécessaire d'avoir dans le fichier json la configuration du barème (cf fichier exemple) pour la fonction de calcul :
```json
"3": [
    {
        "coeff": 0.502,
        "term": 0
    },
    {
        "coeff": 0.3,
        "term": 1007
    },
    {
        "coeff": 0.35,
        "term": 0
    }
],
```

## Mode verbeux
Le mode verbeux fonctionne de la manière suivante :
- absence de l'argument `-v`: seuls les messages de type `ERROR` sont affichés en plus des messages standards.
- `-v` les messages supplémentaires sont affichés à partir du niveau `WARN`
- `-vv` les messages supplémentaires sont affichés à partir du niveau `INFO`
- `-vvv` niveau maximal avec les messages jusqu'au niveau `DEBUG`

## Exemples
### Obtenir l'aide du script
```console
./travel_expenses.py -h
./travel_expenses.py [fonction] -h
```
### Ajouter un déplacement
```console
./travel_expenses.py -vvv add --date 22/10/2022 --distance 62.3
./travel_expenses.py -vvv --history_name hist.json add --date 22/10/2022 --distance 62.3
```
### Obtenir le montant des frais réels pour une année
```console
./travel_expenses.py calculate --year 2022 --power 5
```

# Evolutions à venir
Ce script ne permet actuellement pas :
- de supprimer d'entrée(s) dans l'historique
- de générer des déplacements sur une période donnée afin d'éviter 5 exécutions pour une semaine par exemple

Ces 2 points feront l'objet de mises à jour ultérieures de ce script.