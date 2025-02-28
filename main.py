from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os

# Initialisation de l'application FastAPI
app = FastAPI()

# Clé API OpenAI (assurez-vous de la configurer dans Railway)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Modèle de données pour les requêtes
class TestSubmission(BaseModel):
    user_id: int
    test_id: int
    responses: dict

@app.post("/submit_test")
def submit_test(data: TestSubmission):
    try:
        # Génération de la demande d'évaluation
        prompt = "Évalue ces réponses de test de soft skills et attribue une note sur 100 à chaque question :\n"
        for q, r in data.responses.items():
            prompt += f"Question: {q}\nRéponse: {r}\n\n"
        
        # Appel à OpenAI pour générer l'évaluation
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un évaluateur expert en soft skills."},
                {"role": "user", "content": prompt}
            ]
        )
        
        evaluation = response["choices"][0]["message"]["content"]
        
        return {"user_id": data.user_id, "test_id": data.test_id, "evaluation": evaluation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route de test
@app.get("/")
def read_root():
    return {"message": "API FastAPI de test de soft skills en ligne !"}
