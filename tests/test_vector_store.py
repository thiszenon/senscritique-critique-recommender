"""
Test de la class VectorStore,
Test generé par l'ia 
Auteur : Jo kabonga
Date : 3/11/2025

"""
import pytest 
import numpy as np
import pandas as pd
from src.vector_store.vector_store import VectorStore

class TestVectoreStore:
    def test_init(self):
        """Test initialisation de la classe VectoreStore"""
        vector_store = VectorStore()
        assert vector_store.loaded_films == {}
        assert vector_store.data_path.exists()
    #end test_init

    def test_film_exists(self):
        """ Test si films existent """
        vector_store = VectorStore()
        assert vector_store.film_exists("fightclub") == True 
        assert vector_store.film_exists("film qui n'existe pas ") == False
    #end test_film_exists

    def test_load_film(self):
        """Test chargement d'un film """
        vector_store = VectorStore()
        film_data = vector_store.load_film("fightclub")
        assert 'embeddings' in film_data
        assert 'metadata' in film_data
        assert len(film_data['embeddings']) == len(film_data['metadata'])
    #end test_load_film

    def test_search_similar_vectors(self):
        """Test rcherche similarités"""
        vector_store = VectorStore()
        film_data = vector_store.load_film("fightclub")
        vecteur_ref = film_data['embeddings'][0] 
        scores, indices = vector_store.search_similar_vectors("fightclub",vecteur_ref,k=5)
        assert len(scores) == 6 # k+1 avant le filtre de l'auto-recommandation
        assert len(indices) == 6
        assert all(score <=1.0 for score in scores) # le score de similarité doit etre compris entre 1 et 0

