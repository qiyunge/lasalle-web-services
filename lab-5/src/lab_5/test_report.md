# Tests — client icanhazdadjoke (lab-5)


## Cas	Entrée	Résultat observé	Problème corrigé
1. Recherche directe, page 1
python3 test_api.py avec term=cat, page=1, limit=10
HTTP 200, URL https://icanhazdadjoke.com/search?term=cat&page=1&limit=10, puis plantage : KeyError: 'page'
Le JSON n’a pas de clé page. Lecture changée pour current_page.

2. Recherche directe, page 1 (après correction)
mêmes paramètres
HTTP 200, page 1, total 11, 10 blagues affichées


3. Recherche directe, page 2
term=cat, page=2, limit=10
HTTP 200, page 2, total 11, 1 blague affichée

4. Lancement du client
uv run lab-5
TypeError: 'module' object is not callable dans .venv/bin/lab-5
Le point d’entrée lab_5:main importait le module main.py. Corrigé en lab_5.main:main, puis reconstruction du paquet.
Menu, recherche
choix 2, terme cat, puis q
Page 1 de 3, total 11, 5 blagues avec identifiant, retour au menu

5. Quitter
choix 0
Affiche Au revoir! et termine

6. Dépendances
pip freeze et python3 -m pip freeze
pip absent
requirements.txt produit avec uv export --format requirements-txt --no-dev --no-hashes (requests==2.34.2 et ses dépendances)