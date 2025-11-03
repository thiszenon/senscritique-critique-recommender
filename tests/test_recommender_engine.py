"""
Test de la class RecommenderEngine,
Test generé par l'ia 
Auteur : Jo kabonga
Date : 3/11/2025

"""

import pytest
from src.recommandation.recommender_engine import RecommanderEngine
from src.vector_store.vector_store import VectorStore

class TestRecommenderEngine:
    @pytest.fixture
    def engine(self):
        """Fixture pour initialiser le moteur"""
        vector_store = VectorStore()
        return RecommanderEngine(vector_store)
    
    def test_init(self, engine):
        """Test initialisation RecommenderEngine"""
        assert engine.vector_store is not None
    
    def test_get_index_with_id_valid(self, engine):
        """Test recherche index avec ID valide"""
        index = engine._get_index_with_id("fightclub", "20761")
        assert index is not None
        assert isinstance(int(index), int)
    
    def test_get_index_with_id_invalid(self, engine):
        """Test recherche index avec ID invalide"""
        index = engine._get_index_with_id("fightclub", "999999")
        assert index is None
    
    def test_find_similar_basic(self, engine):
        """Test recherche similarités basique"""
        resultats = engine.find_similar(
            critique_id="20761",
            film_id="fightclub", 
            k=3,
            scores_sim_min=0.7
        )
        assert len(resultats) <= 3
        assert 'similarity_score' in resultats.columns
        assert 'user_id' in resultats.columns
    
    def test_find_similar_auto_recommendation_filtered(self, engine):
        """Test que l'auto-recommandation est filtrée"""
        resultats = engine.find_similar(
            critique_id="20761",
            film_id="fightclub",
            k=10
        )
        if len(resultats) > 0:
            assert 'similarity_score' in resultats.columns
            # Vérifier qu'aucun résultat n'a un score de 1.0 (auto-reco)
            assert all(resultats['similarity_score'] < 1.0)
        else:
            pytest.skip("aucune critique similaire retrouvée ")