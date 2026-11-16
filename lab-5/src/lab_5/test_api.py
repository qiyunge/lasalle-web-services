import requests


url = "https://icanhazdadjoke.com/"
headers = {
    "Accept": "application/json",
    "User-Agent": "Python/3.12.7"
}

params = {
    "term": "cat",
    "page": 2,
    "limit": 10
}

url = "https://icanhazdadjoke.com/search"
response = requests.get(
    url, 
    headers=headers, 
    params=params,
    timeout=10)
print("Code Http :", response.status_code)
response.raise_for_status()
donnees = response.json()

print("URL envoyée :", response.url)
print("Page :", donnees["current_page"])
print("Total :", donnees["total_jokes"])

for blague in donnees["results"]:
    print("Blague :", blague["joke"])
    print("--------------------------------")