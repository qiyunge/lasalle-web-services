# Lab 03 — API REST Flask avec SQLite

Projet pédagogique de gestion d’un collège : programmes, étudiants, cours et inscriptions.

L’application utilise Flask et SQLite, avec une architecture hexagonale séparant le domaine, les cas d’utilisation et les adaptateurs techniques.

## Technologies

- Python 3.12
- Flask et Blueprint
- SQLite
- uv
- Pyright
- Ruff
- pytest

## Installation

Depuis la racine du projet :

```bash
uv sync
```

## Démarrage

```bash
uv run python -m lab_3.main
```

L’API est accessible à l’adresse :

```text
http://127.0.0.1:5000
```

La connexion et l’initialisation de la base sont configurées dans les modules `bootstrap/database.py` et `adapters/outbound/sqlite/connection.py`.

## Architecture

```text
src/lab_3/
├── core/
│   ├── domain/
│   │   ├── common/
│   │   ├── value_objects/
│   │   ├── programme.py
│   │   ├── student.py
│   │   ├── cours.py
│   │   └── inscription.py
│   └── application/
│       ├── bus/
│       ├── ports/
│       │   ├── inbound/
│       │   └── outbound/
│       └── services/
├── adapters/
│   ├── inbound/flask/
│   └── outbound/sqlite/
├── bootstrap/
└── main.py
```

### Domaine

Les entités et objets-valeurs représentent les concepts métier et leurs règles de validation. Ils ne dépendent ni de Flask ni de SQLite.

Les méthodes `create()` et `restore()` distinguent la création d’une nouvelle entité de la reconstruction d’une entité persistée.

### Application

Les handlers exécutent les cas d’utilisation et dépendent des ports de sortie.

- Les ports d’entrée définissent les commandes, requêtes, résultats et erreurs métier.
- Les ports de sortie définissent les contrats des repositories et de l’unité de travail.
- Un bus commun distribue les commandes et les requêtes à leurs handlers.

### Adaptateurs

L’adaptateur Flask traite les requêtes HTTP, valide leur structure et transforme les données en objets attendus par l’application.

L’adaptateur SQLite exécute les opérations SQL et reconstruit les entités à partir des données persistées.

### Bootstrap

Les modules de bootstrap construisent les dépendances, enregistrent les handlers et les Blueprints, puis assemblent l’application.

## Modèle de données

| Table | Rôle |
|---|---|
| `PROGRAMMES` | Programmes d’études |
| `STUDENTS` | Étudiants rattachés à un programme |
| `COURS` | Cours proposés |
| `INSCRIPTIONS` | Association entre un étudiant et un cours, avec une note facultative |

Un programme possède plusieurs étudiants. Les étudiants et les cours sont liés par les inscriptions.

La contrainte unique sur `(student_id, cours_id)` empêche une double inscription au même cours. Les clés étrangères sont activées pour chaque connexion SQLite.

## Validation et erreurs

La validation s’effectue à plusieurs niveaux :

- Le parsing HTTP vérifie la présence des champs et leurs types.
- Les objets-valeurs vérifient la validité des valeurs métier.
- Les handlers vérifient les conditions du cas d’utilisation.
- Les contraintes SQLite garantissent l’intégrité des données lors de l’écriture.

Les échecs métier attendus sont représentés par `Result`, composé de `Success` et `Failure`.

Les incidents techniques sont représentés par des exceptions. Les conflits explicitement récupérables peuvent déclencher un nombre limité de nouvelles tentatives.

## Transactions

Chaque unité de travail ouvre une connexion et démarre une transaction.

- Le handler appelle explicitement `commit()` pour valider les écritures.
- Toute transaction encore active à la sortie est annulée.
- La connexion est ensuite fermée.
- Les repositories d’une même unité de travail utilisent la même connexion, obtenue via un provider et `ContextVar`.

Les lectures utilisent également une unité de travail pour gérer la durée de vie de la connexion.

## État d’avancement

Le code des fonctionnalités suivantes a été travaillé :

- Création d’une inscription.
- Modification ou suppression de sa note.
- Suppression d’une inscription.
- Consultation de la liste des programmes.

La création d’un programme est en cours.

Cette liste ne constitue pas une confirmation de réussite de tous les tests.

## Interfaces prévues par le laboratoire

Les chemins ci-dessous correspondent à l’énoncé. Cette section décrit le périmètre cible ; elle ne signifie pas que tous les endpoints sont déjà implémentés.

| Méthode | Chemin | Fonction |
|---|---|---|
| POST | `/programmes` | Créer un programme |
| GET | `/programmes` | Lister les programmes |
| POST | `/etudiants` | Créer un étudiant |
| GET | `/etudiants` | Lister les étudiants |
| GET | `/etudiants/<id>` | Consulter un étudiant |
| GET | `/etudiants/<id>/cours` | Consulter ses cours |
| POST | `/cours` | Créer un cours |
| GET | `/cours` | Lister les cours |
| GET | `/cours/<id>/etudiants` | Consulter les étudiants d’un cours |
| POST | `/inscriptions` | Inscrire un étudiant à un cours |
| PATCH | `/inscriptions/<id>` | Modifier une note |
| DELETE | `/inscriptions/<id>` | Supprimer une inscription |
| GET | `/etudiants/<id>/releve` | Consulter le relevé d’un étudiant |

Le filtre `GET /etudiants?programme=1` fait partie de la consultation de la liste des étudiants.

## Exemples de requêtes

### Créer une inscription

Les identifiants doivent correspondre à des données existantes.

```http
POST /inscriptions/
Content-Type: application/json

{
  "student_id": 1,
  "cours_id": 1
}
```

### Modifier une note

Remplacer `42` par l’identifiant réel de l’inscription.

```http
PATCH /inscriptions/42
Content-Type: application/json

{
  "note": 85
}
```

La note doit être comprise entre 0 et 100.

L’application prévoit également la possibilité de retirer une note :

```json
{
  "note": null
}
```

Un champ `note` absent constitue une requête invalide.

### Supprimer une inscription

```http
DELETE /inscriptions/42
```

Aucun corps JSON n’est nécessaire.

### Lister les programmes

```http
GET /programmes
```

Une liste vide est un résultat valide et retourne le statut 200.

## Qualité du code

Vérification des types :

```bash
uv run pyright
```

Analyse du code :

```bash
uv run ruff check .
```

Correction automatique des problèmes compatibles :

```bash
uv run ruff check . --fix
```

Formatage :

```bash
uv run ruff format .
```

Exécution des tests :

```bash
uv run pytest
```