
"""
Ici, on fait la gestion de dependances et initialiser l'api une fois au demarrage
Auteur :Jo kabonga
Date:2/11/2025
"""
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
#configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s- %(message)s'
)

logger = logging.getLogger(__name__)

from recommandation.recommender_engine import RecommanderEngine
from vector_store.vector_store import VectorStore

def get_recommender():
    """
    initialisation du système
    Returns:
        recommander_engine : moteur de recommandation
    """

    try:
        logger.info("Initialisation du système ...")

        # initialisation de la class  VectorStore

        vector_store = VectorStore()
        logger.info("vectorStore initialisé...")

        # le moteur de recommandation
        engine_R = RecommanderEngine(vector_store)
        logger.info("RecommanderEngine initialisé...")

        # films disponible
        films = vector_store.list_available_films()
        logger.info("Films disponible ")

        logger.info("systeme prêt")
        return engine_R
    
    except Exception as ex:
        logger.error(f"erreur initialiation: {ex}")
        raise

recommender_engine = get_recommender()




