
"""
utilisation de FastAPI , endpoint principal pour trouver des critiques similaires

Auteur: Jo kabonga
Date: 2/11/2025
"""

from fastapi import FastAPI, HTTPException
import logging
import time
from typing import List

# importation des modules
from src.schemas.models import CritiqueReference, RecommandationRequest, RecommendationResponse,CritiqueResponse
from src.api.dependencies import recommender_engine

#Config du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s- %(message)s'
)
logger = logging.getLogger(__name__)

#app

app = FastAPI(
    title = "SensCritique Recommendation API",
    description = "API de recommandation de critiques similaires "
)

@app.post("/recommendations", response_model=RecommendationResponse)
def get_recommendations(request: RecommandationRequest):
    """
    endpoint principal - retourne les critiques à une critique donnée
    """
    start_time = time.time() # pour analyser le temps des requetes

    try:
        logger.info(f"requete: film='{request.film_id}', critique='{request.critique_id}', k={request.k}")

        # appel au moteur
        critiques_similaires = recommender_engine.find_similar(
            critique_id = request.critique_id,
            film_id = request.film_id,
            k=request.k,
            scores_sim_min = 0.7 # à ajuster
        )
        process_time = time.time() - start_time

        # recup les infos
        film_id_normalizer = request.film_id.lower().strip()
        film_data = recommender_engine.vector_store.load_film(film_id_normalizer)
        dataF_metadata = film_data['metadata']

        #trouver la critique de ref
        critique_ref = dataF_metadata[dataF_metadata['id'] == int(request.critique_id)].iloc[0]

        #construction de la rep
        response = RecommendationResponse(
            critique_reference = CritiqueReference(
                id=request.critique_id,
                film=request.film_id,
                user_id = str(critique_ref['user_id'])
            ),

            recommendations=[
                CritiqueResponse(
                    id=str(row['id']),
                    user_id = str(row['user_id']),
                    score_similarity = round(row['similarity_score'],4),
                    review_content = row['review_content']
                )
                for _, row in critiques_similaires.iterrows()

            ],
            metadata={
                "total_results": len(critiques_similaires),
                "temps_exec": f"{process_time:.3f}s",
                "film": request.film_id
            }
        )

        logger.info(f"requete traitée: {len(critiques_similaires)} resultats en {process_time:.3f}s")
        return response
    
    except ValueError as ex:
        # critique ou film non trouvé
        logger.warning(f"{str(ex)}")
        raise HTTPException(status_code=404, detail=str(ex))
    except Exception as ex:
        # erreur dans la fonction
        logger.error(f"erreur : {ex}")
        raise HTTPException(status_code = 500, detail="erreur interne et/ou serveur")
#end get_recommendations

@app.get("/health")
def health_check():
    """
    verifier le fonctionnement de l'api, à revoir
    """
    return {
        "status": "healthy",
        "service":"SensCritique recommendation API",
        "auteur": "Jo Kabonga",
        "ref": "cet espace est à toi à condition de l'accompagner d'un petit drink"

    }
#end health_check

@app.get("/films")
def list_films():
    """
    Liste de tous les films disponibles pour les recommandations
    """
    try:
        films = recommender_engine.vector_store.list_available_films()

        return {"films_dispo": films}
    except Exception as ex:
        logger.error(f"erreur liste films: {ex}")
        return {"films_dispo": [] }
#end list_films

@app.get("/")
def root():
    """Page d'accueil de l'api """
    return {
        "message": "Bienvenue sur l'API SensCritique recommandation",
        "description": "recommandation de critiques similaires ",
        "endspoints": {
            "documentation": "/docs",
            "santé": "/health",
            "films": "/films",
            "recommandations": "POST /recommendations"
        }
    }
#end root
    
    

