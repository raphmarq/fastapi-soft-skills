from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os

# Initialisation de l'application FastAPI
app = FastAPI()

# Configuration CORS pour accepter uniquement les requêtes de raph.so
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://www.raph.so", "https://www.raph.so"],  # Autorise uniquement raph.so
    allow_credentials=True,
    allow_methods=["POST", "GET"],  # N'autorise que les méthodes nécessaires
    allow_headers=["Content-Type"],  # Autorise uniquement les en-têtes utiles
)

# Vérification de la clé API OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("La clé API OpenAI n'est pas définie.")
client = openai.OpenAI(api_key=api_key)

# Modèle de données pour les requêtes
class TestSubmission(BaseModel):
    user_id: int
    test_id: int
    responses: dict

@app.post("/submit_test")
def submit_test(data: TestSubmission):
    try:
        print("Réception des données:", data.dict())  # Debug
        prompt = """
Tu es un expert en évaluation des soft skills. 
Analyse chaque réponse selon ces critères :
- **Clarté** : La réponse est-elle bien formulée et compréhensible ?
- **Cohérence** : La réponse est-elle logique par rapport à la question ?
- **Pertinence** : Apporte-t-elle une vraie information utile ?
- **Créativité** : Montre-t-elle une réflexion originale ?
- **Capacité de réflexion** : Démontre-t-elle un raisonnement structuré ?

Attribue une note sur 100 en justifiant brièvement ton évaluation.
Format attendu :
- Score global : XX/100
- Justification : [2 phrases maximum]

Voici les réponses à analyser :
"""
for q, r in data.responses.items():
    prompt += f"Question: {q}\nRéponse: {r}\n\n"


        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Tu es un évaluateur expert en soft skills."},
                {"role": "user", "content": prompt}
            ]
        )

        evaluation = response.choices[0].message.content
        return {"user_id": data.user_id, "test_id": data.test_id, "evaluation": evaluation}

    except Exception as e:
        print("Erreur dans l'API:", str(e))  # Log dans Railway
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")

# Route de test
@app.get("/")
def read_root():
    return {"message": "API FastAPI de test de soft skills en ligne !"}

# Log des routes disponibles pour le debug
print("Routes disponibles :", [route.path for route in app.routes])
