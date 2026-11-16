import requests

BASE_URL = "https://icanhazdadjoke.com"

headers = {
    "Accept": "application/json",
    "User-Agent": "Python/3.12.7"
}

def appeler_api(chemin, params=None):
    try:
        response = requests.get(
            f"{BASE_URL}/{chemin}", 
            headers=headers, 
            params=params, 
            timeout=10)

        response.raise_for_status()
        donnees = response.json()

        if not isinstance(donnees, dict):
            print("Reponse inattendue:object Json attendu")
            return None
        
        status_code = donnees.get("status", 200)
        if isinstance(status_code, int) and status_code >= 400:
            print(f"Erreur HTTP: {status_code}")
            return None
        
        return donnees
    
    except requests.exceptions.Timeout:
        print("Temps d'attente dépassé")
        return None
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        if status_code == 404:
            print("Ressource non trouvée")
        else:
            print(f"Erreur HTTP: {status_code}")
      
    except requests.exceptions.JSONDecodeError as e:
        print("Le serveur n'a pas renvoyé un objet JSON valide")
    except requests.exceptions.ConnectionError as e:
        print(f"Erreur de connexion: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'appel API: {e}")
    return None


def afficher_blagues(blague):
    print("\nidentifiant: blague:",blague.get("id", "inconnu"))
    print("Blague:",blague.get("joke", "inconnu"))

def obtenir_aleatoire():
    donnees = appeler_api("/")
    if donnees:
        afficher_blagues(donnees)


def obtenir_par_id(id):
    identifiant = input("identifiant de la blague: ").strip()
    if not identifiant or not identifiant.isalnum():
        print("entrer un identifiant avec letters et chiffres")
        return
    donnees = appeler_api(f"/j/{identifiant}")
    if donnees:
        afficher_blagues(donnees)
    else:
        print("Blague non trouvée")


def rechercher():
    terme = input("terme de recherche: ").strip()
    if not terme:
        print("entrer un terme de recherche")
        return

    page = 1
    while True:
        params = {
            "term": terme,
            "page": page,
             "limit": 5,
        }
        donnees = appeler_api("/search", params=params)
        if not donnees:
            print("Erreur lors de la récupération des blagues")
            return
        resultats = donnees.get("results", [])
        if not resultats:
            print("Aucune blague trouvée")
            return
        total_pages = donnees.get("total_pages", 1)
        print(f"\nPage {page} de {total_pages}")
        print("Total de blagues:", donnees.get("total_jokes", 0))

        for numbero,blague in enumerate(resultats, start=1):
            print(f"\nBlague {numbero}:")
            afficher_blagues(blague)
        choix  = input("n = suivante, p = précédente, q = retour : ")
        choix = choix.strip().lower()
        if choix == "n" and page < total_pages:
            page += 1
        elif choix == "p" and page > 1:
            page -= 1
        elif choix == "q":
            return
        else:
            print("choix invalide")

def main():
    while True:
        print("\n ===CLIENT DE LA BLAGUE ===") 
        print("1. Obtenir une blague aléatoire")
        print("2. Rechercher des blagues")
        print("3. Obtenir une blague par identifiant")
        print("0. Quitter")
        choix = input("Entrez votre choix: ").strip().lower()
        if choix == "1":
            obtenir_aleatoire()
        elif choix == "2":
            rechercher()
        elif choix == "3":
            obtenir_par_id()
        elif choix == "0":
            print("Au revoir!")
            break
        else:
            print("Choix invalide. Entrez 0, 1, 2 ou 3.")

if __name__ == "__main__":
    main()