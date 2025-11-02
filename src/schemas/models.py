"""
Utilisation des modèles Pydantic pour l'API 
Objectif: definir la structure des données (requetes/reponses)

Auteur: Jo kabonga
Date: 2/11/2025
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class RecommandationRequest(BaseModel):
    """
    modele pour les requetes de recommandation

    """
    critique_id:str
    film_id:str
    k:int = Field(default=5, ge=1, le=10,description="nombre de resultats entre 1-10") #description generer par ia

class CritiqueReference(BaseModel):
    """modele pour la critique de ref"""
    id:str
    film_id:str
    user_id: Optional[str] = None #ou anonyme à revoir... 

class CritiqueResponse(BaseModel):
    """Modele pour une critique similaire retourné"""
    id: str
    user_id:str
    score_similarity:float
    review_content:str

class RecommandationResponse(BaseModel):
    """ modele pour la reponse complete de recommandation"""
    critique_ref: CritiqueReference 
    recommandations: List[CritiqueResponse]
    metadata: dict


