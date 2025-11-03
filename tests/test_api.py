"""Test du module 4 """



# tests/test_api.py
import pytest
import sys
import os

sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..', 'src'))

from fastapi.testclient  import TestClient
from src.api.main import app

client = TestClient(app=app)

class TestAPI:
    def test_health_endpoint(self):
        """Test endpoint santé"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_films_endpoint(self):
        """Test endpoint films"""
        response = client.get("/films")
        assert response.status_code == 200
        assert "films_dispo" in response.json()
    
    def test_recommendations_valid(self):
        """Test endpoint recommandations avec données valides"""
        response = client.post(
            "/recommendations",
            json={
                "critique_id": "20761",
                "film_id": "fightclub",
                "k": 3
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "critique_reference" in data
        assert "recommendations" in data
        assert "metadata" in data
    
    def test_recommendations_invalid_film(self):
        """Test avec film inexistant"""
        response = client.post(
            "/recommendations",
            json={
                "critique_id": "20761", 
                "film_id": "film_inexistant",
                "k": 3
            }
        )
        assert response.status_code == 404
    
    def test_recommendations_invalid_critique(self):
        """Test avec critique inexistante"""
        response = client.post(
            "/recommendations",
            json={
                "critique_id": "999999",
                "film_id": "fightclub",
                "k": 3
            }
        )
        assert response.status_code == 404