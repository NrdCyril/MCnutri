import requests
import json

def generate_recipe(prompt: str) -> str:
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral",
        "prompt": prompt + """

Réponds UNIQUEMENT avec un JSON valide, sans texte autour, sans balises markdown.
Format exact :
{
  "title": "Nom de la recette",
  "instructions": "Étapes détaillées",
  "ingredients": [
    {"name": "nom_ingredient", "quantite": 150}
  ]
}
""",
        "stream": False
    })
    return response.json()["response"]