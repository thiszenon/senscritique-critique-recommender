import pandas as pd
import logging # pour suivre le déroulement du script 
import sys 
from pathlib import Path

# Configuration du logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
    ) # config générée par ia.

logger = logging.getLogger(__name__) 

def clean_critiques_data(csv_path,film_name):
    """
    Fonction qui nettoie les données en gardant celles utiles au moteur de recommandation

    Args: 
        - csv_path: le chemin du fichier brute csv
        - film_name: le titre du film
    return: df_clean : un dataFrame 

    """
    try:
        # Vérification initiale 
        csv_path = Path(csv_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"Fichier introuvable -> {csv_path}")
        #End if
        
        if csv_path.stat().st_size == 0:
            raise ValueError(f" fichier vide -> {csv_path}")
        #End if

        logger.info(f" Traitement du fichier :{csv_path}")
        
        # Chargement 
        try:
            colonnes_utiles = ['id','review_content','user_id']
            dataF = pd.read_csv(csv_path, usecols=colonnes_utiles) # création du dataFrame avec les colonnes jugées utile
        except KeyError as ex :
            logger.error(f"Colonne manquante dans le fichier csv -> {ex}")
    except Exception as ex:
        logger.error("à completer")
        


        