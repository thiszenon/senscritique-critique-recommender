# SensCritique - Recommandation de Critiques Similaires

## Objectif 
Système de recommandation de critiques similaires pour SensCritique. 

## Architecture 
![System Design](docs/system_design.png)

## Installation 
```bash
git clone https://github.com/thiszenon/senscritique-critique-recommender
cd senscritique-critique-recommender
pip install -r requirements.txt
```
## Utilisation
```python
from src.recommender_engine import RecommenderEngine

engine_R = RecommenderEngine()
recommandations = engine.get_similar_critiques(
critique_id = "2607",
film_id="fight_club"
) 
```
