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

"""TODO: Teste chaque methode apres chaque implementation !!!!!!!!!!"""

def clean_critiques_data(csv_path,film_name):
    """
    Fonction qui nettoie les données en gardant celles utiles au moteur de recommandation

    Args: 
        - csv_path: le chemin du fichier brute csv
        - film_name: le titre du film
    return: dataF_clean : le dataFrame nettoyé 

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
            colonnes_utiles = ['id','review_content','user_id'] # charger que les colonnes utiles 
            dataF = pd.read_csv(csv_path, usecols=colonnes_utiles) # création du dataFrame avec les colonnes jugées utile
        except KeyError as ex :
            logger.error(f"Colonne manquante dans le fichier csv -> {ex}")
            # ou chargement de toutes les colonnes et selectionner après 
            dataF = pd.read_csv(csv_path)
            colonnes_dispo = dataF.columns.to_list()
            logger.info(f"colonnes dispo : {colonnes_dispo}")

            #Verifier les colonnes jugées utiles
            if 'review_content' not in dataF.columns:
                raise ValueError("col 'review_content' manquante")
            # si la colonne review_content existe

            colonnes_utiles = [col  for col in ['id','review_content','user_id'] if col in  dataF.columns]

            dataF = dataF[colonnes_utiles]

        logger.info(f"données initiales: {len(dataF)} lignes, {len(dataF.columns)} colonnes")

        # NETTOYAGE 
        # Supprimer les lignes où review_content manque : inutile pour le moteur
        initial_count = len(dataF) # les données initiales avant suppression

        dataF_clean = dataF[dataF['review_content'].notna()]
        nan_suppr = initial_count - len(dataF_clean) 
        logger.info(f" {nan_suppr} lignes spprimées ")

        # Supprimer les chaines vides
        empty_count = len(dataF_clean)
        dataF_clean = dataF_clean[dataF_clean['review_content'].str.strip() != '']
        empty_suppr = empty_count - len(dataF_clean)
        logger.info(f"{empty_suppr} lignes supprimées")

        # Verfier qu'il y a des données 
        if len(dataF_clean)==0:
            raise ValueError("Aucune données restante")
        #End if

        # Gestion des user_id manquants
        user_id_nan_count = dataF_clean['user_id'].isna().sum() # le nombre d'user_id manquant

        dataF_clean['user_id'] = dataF_clean['user_id'].fillna('anonyme') # remplacer les user_id par anonyme

        if user_id_nan_count > 0:
            logger.info(f"{user_id_nan_count} remplacés par anonymes")
        #End if

        # Ajouter film_id pour avoir les colonnes jugées utiles
        dataF_clean['film_id']= film_name # parametre 

        # Supprimer les doublons exacts 
        data_count = len(dataF_clean) # les données avant suppression des doublons
        dataF_clean = dataF_clean.drop_duplicates(subset='review_content')
        doublons_suppr = data_count - len(dataF_clean)
        logger.info(f"{doublons_suppr} de lignes supprimées")

        """TODO : Rapport final d'avant et apres nettoyage """

        return dataF_clean
    except Exception as ex:
        logger.error(f"Erreur lors du traitement du fichier {csv_path} -> {ex}")
        raise 
#End clean_critiques_data

def validate_cleaned_data(dataF,film_name):
    """
    Fonction de validation des données nettoyées 
    """
    if dataF is  None or len(dataF) == 0:
        raise ValueError(f"dataset vide pour {film_name} remrq: apres nettoyage")
    #End if

    #Verification des colonnes requises
    colonnes_requises = ['review_content','film_id'] # les deux colones importante 
    for col in colonnes_requises:
        if col not in dataF.columns:
            raise ValueError(f"Colonne manquante: {col}")
        #end if
    #end for

    #Verifier le contenu
    if dataF['review_content'].str.strip().eq('').all():
        raise ValueError(f"aucun texte valide pour {film_name}")
    #end if

    logger.info(f"validation réusssi pour {film_name}")
    return True
#end validate_cleaned_data

"""TODO: Sauvegarder les données après nettoyage"""

def save_cleaned_data(dataF, film_name, output_dir = "../../data/processed"):
    """
    Fonction qui sauvegarde les données après nettoyage
    Params:
        - dataF: le dataset
        - film_name : le nom du film
        - output_dir: chemin par defaut de la sauvegarde
    """
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True) # générer par ia 

        # Sauvegarder en CSV
        csv_path= output_path/f"{film_name}_cleaned.csv"
        dataF.to_csv(csv_path, index = False, encoding='utf-8')

        #Info
        logger.info(f"Donées sauvergardées: ")
        logger.info(f" {csv_path}")

        return csv_path
    except Exception as ex:
        logger.error(f"erreur lors de la sauvergarde -> {ex}")
        raise
#end save_cleaned_data

if __name__ =="__main__":
    try:
        #Nettoyage 
        logger.info("Nettoyage ...")
        data_fightclub= clean_critiques_data("../../data/fightclub_critiques.csv","fightclub")
        validate_cleaned_data(data_fightclub,"fightclub")

        data_interstellar = clean_critiques_data("../../data/interstellar_critique.csv","interstellar")
        validate_cleaned_data(data_interstellar,"interstellar")

        # sauvegarde les données
        logger.info("Sauvegarde de données...")
        save_cleaned_data(data_fightclub,"fightclub")
        save_cleaned_data(data_interstellar,"interstellar")

        logger.info("Nettoyage et sauvegarde reussie")
    except Exception as ex:
        logger.error(f"erreur -> {ex}")
        sys.exit(1)



    



        


        