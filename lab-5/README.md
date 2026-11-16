# Lab 5 — Client de l'API icanhazdadjoke

Petit client en ligne de commande qui interroge [icanhazdadjoke](https://icanhazdadjoke.com/) et affiche des blagues.

## Technologies

- Python 3.12
- requests
- uv

## Installation

Depuis le dossier `lab-5` :

```bash
uv sync
```

## Démarrage

```bash
uv run lab-5
```

Le menu propose quatre choix :

1. Obtenir une blague aléatoire
2. Rechercher des blagues (pagination avec `n`, `p` et `q`)
3. Obtenir une blague par identifiant
0. Quitter

## Fichiers

- `src/lab_5/main.py` : client et menu
- `src/lab_5/test_api.py` : essai direct de la recherche
- `pyproject.toml` : dépendances et commande `lab-5`
