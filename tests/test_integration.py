# tests/test_integration.py
import pytest
from src.vector_store.vector_store import VectorStore
from src.recommandation.recommender_engine import RecommanderEngine
from src.api.dependencies import get_recommender

class TestIntegration:
    def test_pipeline(self):
        """Test du pipeline complet"""
        # 1. Initialisation
        vector_store = VectorStore()
        engine = RecommanderEngine(vector_store)
        
        # 2. Recherche
        resultats = engine.find_similar(
            critique_id="20761",
            film_id="fightclub",
            k=5,
            scores_sim_min=0.5
        )
        
        # 3. Vérifications
        assert len(resultats) > 0
        assert all(col in resultats.columns for col in ['id', 'user_id', 'similarity_score', 'review_content'])
        
        # 4. Vérifier que les scores sont cohérents
        assert all(0.5 <= score <= 1.0 for score in resultats['similarity_score'])