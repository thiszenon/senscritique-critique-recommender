
"""
Ici , on genere les vecteus (embeddings) pour les critiques de films
Docs : https://www.sbert.net/
Auteur: Jo Kabonga
Date: 30/10/2025
"""
import pandas as pd
import numpy as np 
import logging 
from sentence_transformers import SentenceTransformer
from pathlib import Path
import sys

# configuration du logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
) # config générer par l'ia

logger = logging.getLogger(__name__)

class Embedding:
    """
    Classe pour transformer le texte en vecteurs numériques

    Explication: utilisation d'un modèle pré-entraîné pour comprendre le sens 
    semantique du texte et le rprésenter sous forme de vecteurs.

    SOURCE: Sentence-BERT (SBERT) - modèle spécialisé dans la similarité sémantique

    """

    def __init__(self,model_name='all-MiniLM-L6-v2'):
        """
        Initialisation du modèle d'embedding
        Args:
            model_name:nom du modèle sentence-transformers.
                - all-MiniLM-L6-v2 : équilibré, rapide, bon pour le français et l'anglais
                - dimensions: 384 bonne précision

        """
        try:
            logger.info(f"Chargement du modèle:{model_name}")
            self.model = SentenceTransformer(model_name) # charger le model
            self.dim_embedding = self.model.get_sentence_embedding_dimension() # la dimenson des vecteurs
            logger.info(f"model chargé - dimension des embeddings = {self.dim_embedding}")

        except Exception as ex:
            logger.error(f"erreur lors du chargement du model: {ex}")
            raise
    #end __init__

    def embeddings_generer(self,texts,batch_size=32, show_progress=True):
        """
        Generer les vecteurs pour une liste de textes

        Args:
            texts (list): liste des textes à encoder
            batch_size(int): taille des lots, limiter à 32 pour la memoire
            show_progress (bool): afficher une barre de progress

        Returns: 
            np.array : matrice des vecteurs de n_texts,dim_embeddings
        """

        try:
            # verifier les données
            if not texts or len(texts) == 0:
                raise ValueError("textes vide")
            #end if
            logger.info(f"generation des vecteurs pour {len(texts)} textes")

            #encodage par lots (optimisation mémoire ou pas )
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar = show_progress,
                convert_to_tensor = False, # retourner au format numpy array pour utiliser FAISS
                normalize_embeddings = True # pour la similarité cosinus
            )
            logger.info(f"Vecteurs générés: {embeddings.shape}")

            return embeddings
        except Exception as ex:
            logger.error(f"erreur de la generation des vecteurs: {ex}")
            raise
    #end embeddings_generer

    def process_dataF(self,dataF, text_column='review_content'):
        """
        Traite le dataF et genere les vecteurs

        Args:
            dataF : dataFrame avec les colonnes de texte
            text_column: colonne avec le texte à encoder

        Returns:
            tuple:(DataFrame avec les vecteurs, matrices d'emeddings)
        """
        try:
            #verifier de la colonne texte
            if text_column not in dataF.columns:
                raise ValueError(f"colonne '{text_column}' non trouvée dans le DataF ")
            #end if

            #extraction des textes
            texts = dataF[text_column].tolist()

            logger.info(f"Traitement du dataF: {len(dataF)} lignes, colonne'{text_column}")
            embeddings = self.embeddings_generer(texts=texts)
            
            # ajouter les vecteurs au dataF
            dataF_embeddings = dataF.copy()
            dataF_embeddings['embedding'] = list(embeddings)

            logger.info(f"dataF mis à jour : {len(dataF_embeddings)} lignes avec les vecteurs")
            return dataF_embeddings,embeddings
        except Exception as ex:
            logger.error(f"ereur du traitement du dataF: {ex}")
            raise

    #end process_dataF

def main():
    try:
        logger.info("Generation des vecteurs")

        from data_cleaner import clean_critiques_data
        
        # chargement et nettoyage 
        logger.info("chargement des données")
        dataF_fightclub = clean_critiques_data("../../data/fightclub_critiques.csv","fightclub")
        dataF_interstellar = clean_critiques_data("../../data/interstellar_critique.csv","interstellar")

        # initialisation du model 
        logger.info("Initialisation du model")
        embeddings_generer = Embedding() # appel de la classe 

        #génération des vecteurs
        logger.info("génération des vecteurs")

        #Fight Club
        dataF_fightclub_emb, emb_fightclub = embeddings_generer.process_dataF(dataF_fightclub)
        #Interstellar
        dataF_interstellar_emb, emb_interstellar = embeddings_generer.process_dataF(dataF_interstellar)

        #sauvegarde
        logger.info("Sauvegarde des resultats")
        output_dir = Path("../../data/processed")
        output_dir.mkdir(exist_ok=True)
        dataF_fightclub_emb.to_pickle(output_dir/"fightclub_avec_embeddings.pkl")
        dataF_interstellar_emb.to_pickle(output_dir/"interstellar_avec_embeddings.pkl")

        #sauvegarde des matrices des vecteurs pour une utilisation avec FAISS ou pas 
        np.save(output_dir/"fightclub_avec_embeddings.npy",emb_fightclub)
        np.save(output_dir/ "interstellar_avec_embeddings.npy", emb_interstellar)

        """TODO: RAPPORT FINAL"""
        logger.info(f" Fight club: {len(dataF_fightclub_emb)} critiques -> {emb_fightclub.shape}")
        logger.info(f" Interstellar: {len(dataF_interstellar_emb)} critiques -> {emb_interstellar.shape}")
        logger.info(f" dimensions des vecteurs : {embeddings_generer.dim_embedding}")

        logger.info(f" fichiers sauvegardés dans : {output_dir}")

        ex_emb = emb_fightclub[0]
        logger.info(f" exemple des vecteurs: {ex_emb[:10]}...") # 10 premieres valeurs

        logger.info("generation terminées")
        return dataF_fightclub_emb, dataF_interstellar_emb
    except Exception as ex:
        logger.error(f" Erreur importante : {ex}")
        sys.exit(1)
#end main

if __name__ == "__main__":
    main()




