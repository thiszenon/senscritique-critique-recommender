# SensCritique - Recommandation de Critiques Similaires

Système de recommandation de critiques similaires utilisant le modèle de traitement du langage Sentence-Bert

## Contexte Métier
Permettre aux utilisateurs de découvrir des critiques similaires pendant la lecture d'un avis sur un film.


## Architecture 
** [Voir l'artitecture detaillée et flux de données ici](ARCHITECTURE.md)

![System Design](docs/architecture.png)


## Installation 
```bash
git clone https://github.com/thiszenon/senscritique-critique-recommender
cd senscritique-critique-recommender
pip install -r requirements.txt

python run_api.py 
```

## Utilisation rapide

```python
from src.recommendation.recommender_engine import RecommenderEngine
from src.vector_store.vector_store import VectorStore

#Initialisation
vector_store = VectorStore()
engine_R = RecommenderEngine()

#recherche
recommandations = engine_R.find_similar(
critique_id = "20761",
film_id="fightclub",
k=5,
) 
```

