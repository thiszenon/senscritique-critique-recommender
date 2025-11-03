"""
Ici, on gère le stockage et la recherche des vecteurs de critiques

Auteur: Jo Kabonga
Date: 31/10/2025

"""

import numpy as np
import pandas as pd
import logging
from sentence_transformers import util # pour le calcul du cosinus de simularité
from pathlib import Path 

#Configuration du logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger  = logging.getLogger(__name__)

class VectorStore:
    """
    Classe pour stocker et rechercher les vecteurs de critiques(process fait dans Embedding)
    Expl: utilisation de similarité cosinus directe pour trouver
        les critiques similaires .
    """

    def __init__(self,data_path=None):
        try:
            self.loaded_films = {} # {film_id: {"embeddings:..., "metadata":...}}
            if data_path is None:
                self.data_path = Path(__file__).parent.parent.parent / "data" / "processed"
            else:
                self.data_path = Path(data_path) # chemin où se trouve les données
            logger.info("stockage de vecteurs initialisé et chargement des données")
            
        except Exception as ex:
            logger.error(f"erreur de l'initialisation :{ex}")
            raise 
    #end __init__

    def film_exists(self,film_id:str) -> bool:
        """verifier si un film existe avant le processus du chargement"""
        film_id_normalizer = film_id.lower().strip()
        film_path = self.data_path / film_id_normalizer
        return film_path.exists()
    #end film_exists

    def load_film(self,film_id:str):
        """
        Méthode qui charge un film s'il n'est pas déjà chargé

        """
        try:
            #Normaloisation du nom de films 
            film_id_normaliser = film_id.lower().strip()

            if film_id_normaliser not in self.loaded_films:
                film_path = self.data_path / film_id

                #verifier si le film existe
                if not film_path.exists():
                    raise ValueError(f"film '{film_id}' non trouvé dans {film_path}")
                #end if

                #chemin
                embeddings_path = film_path /"embeddings.npy"
                dataF_metadata_path = film_path / "metadata.pkl"

                # verifier les fichiers chargés
                if not embeddings_path.exists():
                    raise ValueError(f"fichier embeddings manquant :{embeddings_path}")
                #end if
                if not dataF_metadata_path.exists():
                    raise ValueError(f"fichier metadata manquant: {dataF_metadata_path}")
                #end if

                #chargement
                embeddings = np.load(embeddings_path)
                dataF_metadata = pd.read_pickle(dataF_metadata_path)

                #verifier la cohérence des fichiers chargés
                if len(embeddings) != len(dataF_metadata):
                    raise ValueError("incoherence de données...")
                #end if

                #stockage
                self.loaded_films[film_id] = {
                    'embeddings': embeddings,
                    'metadata': dataF_metadata
                }
                logger.info(f"film '{film_id}' chargé et comporte {len(embeddings)} critiques")

            return self.loaded_films[film_id]
            #end if
        except Exception as ex:
            logger.error(f"erreur chargement film '{film_id}' : {ex}")
            raise
    #end load_film


    def add_film(self,film_id,emb_films,dataF_emb_films):
        """
        Ajouter les vecteurs et les metadonnées d'un film
        Args:
            film_id: ID du film
            emb_film : matrice des vecteurs de critiques (process dans Embedding)
            dataF_emb_film: dataFrame avec les métadonnées (----idem----)
        """
        try:
            #verification des données
            if len(emb_films) != len(dataF_emb_films):
                raise ValueError("Nombre de vecteurs diff de metadonnées(incompatible)")
            #end if
            self.loaded_films['film_id']= {
                'embeddings': emb_films,
                'metadata': dataF_emb_films
            }
            logger.info(f"film '{film_id}' ajouté et contient: {len(emb_films)} critiques")
        except Exception as ex:
            logger.error(f"erreur ajout du film {film_id}: {ex}")
            raise
    #end add_film

    def search_similar_vectors(self,film_id,vecteur_ref,k=10):
        """
        Recherche les vecteurs similaires (critiques) pour un film
        Args:
            film_id: film pour lequel la recherche est faite
            vecteur_ref: vecteur de la critique de reference 
            k: nombre de resultat à retourner
            TODO: analyse le temps suite à k !!! 
        Returns:
            tuple:(scores_similarity, indices_results)
        """

        try:
            #chargement du film
            film_data = self.load_film(film_id)
            embeddings = film_data['embeddings']

            #calcul des similarités cosinus
            scores_similarity = util.cos_sim(vecteur_ref,embeddings)[0] # docs:

            #recup des k resultats
            scores_k, indices_k = scores_similarity.topk(k=min(k+1,len(scores_similarity)))

            logger.info(f"recherche '{film_id}' : {len(indices_k)} résultats trouvés")

            return scores_k.numpy(), indices_k.numpy() 
        except Exception as ex:
            logger.error(f"erreur recherche '{film_id}' : {ex}")
            raise
    #end search_similar_vectors
    #Avec seuil de similarité minimu 

    def get_critique_metadata(self,film_id,indices):
        """
        recuperer les metadonnées des critiques
        Args:
            film_id: ID du film
            indices : indices des critiques (op de search_similar_vectors)
        Returns:
            DataF: métadonnées des critiques 

        """
        try:
            film_data = self.load_film(film_id)
            return film_data['metadata'].iloc[indices].copy() # 
        except Exception as ex:
            logger.error(f"erreur recup métadonnées du film '{film_id}': {ex}")
            raise
    #end get_critique_metadata

    def get_film_metadata(self, film_id:str):
        """recuperer toutes les metadata d'un film"""
        try:
            film_data = self.load_film(film_id)
            return film_data['metadata']
        except Exception as ex:
            logger.error(f"erreur métadonnées du film : {film_id}: {ex}")
            raise
    #end get_film_metadata

    #méthodes à ajouter :
    # films disponibles
    def list_available_films(self):
        """Liste de tous les films disponibles"""
        try:
            films =[film.name for film in self.data_path.iterdir() if film.is_dir()] # à revoir si erreur
            logger.info(f"films disponibles: {films}")
            return films
        except Exception as ex:
            logger.error(f"erreur liste films: {ex}")
            return []
    #end list_available_films

    def load_files(self,film_id,path_vecteurs,path_metadata):
        """
        charge les données d'un film depuis les fichiers (data/processed)
        Args:
            film_id: ID du film
            path_vecteurs: chemin vers le fichier .npy
            path_metadata: chemin vers le fichier .pkl
        """

        try:
            logger.info(f"chargement du film '{film_id}' ")
            #chargement des vecteurs
            vectors = np.load(path_vecteurs) # verifier np.load(opti.)

            #chargement des metadonnées
            dataF_metadata = pd.read_pickle(path_metadata)

            # ajouter au stockage
            self.add_film(film_id,vectors,dataF_metadata)
            logger.info(f"film '{film_id}' chargé: {len(vectors)} critiques")

        except Exception as ex:
            logger.error(f"erreur du chargement '{film_id}' : {ex}")
            raise
    #end load_files

def main():
    """
    voir les 10 critiques similaires
    """
    try:
        print("LES CRITIQUES SIMILAIRES")
        #Initialisation
        vector_store =VectorStore() # appel de la classe VectorStore

        # les films dispo

        films= vector_store.list_available_films()
        print(f"films disponibles: {films}")

        film_test = "fightclub1" 

        if film_test:
            print(f"\n Test avec le film : {film_test}")
            #chargement
            film_data = vector_store.load_film(film_test)
            dataF_metadata = film_data['metadata']

            #critique de ref
            critique_ref_index = 200 # essaie d'autre après 
            critique_ref = dataF_metadata.iloc[critique_ref_index]
            print(f"critique de ref (index {critique_ref_index}):")
            print(f"Contenu: {critique_ref['review_content'][:150]}")
            print(f"Film : {critique_ref['film_id']}")

            #recherche similarités
            vecteur_ref  = film_data['embeddings'][critique_ref_index]

            scores, indices = vector_store.search_similar_vectors(film_test,vecteur_ref,k=10)
            print(f"\n {len(scores)} critiques similaires trouvés:")
            for i, (score,idx) in enumerate(zip(scores,indices)):
                if idx != critique_ref_index : # auto-recommandation exclue
                    critique_sim = vector_store.get_critique_metadata(film_test,[idx]).iloc[0]
                    print(f"{i} . similarité: {score:.4f}")
                    print(f"contenu: {critique_sim['review_content'][:150]}...")
                    print(f"user_id: {critique_sim['user_id']}")
                #end if
            #end for

            #structure de données
            print(f"\n Structure du DataFrame: ")
            print(f"Colonnes: {dataF_metadata.columns.tolist()}")
            print(f"nombre de critiques: {len(dataF_metadata)}")
        #end if
        else:
            print(f" {film_test} pas dispo")
    except Exception as ex:
        logger.error(f"erreur dans main: {ex}")
        raise
#end main

if __name__ == "__main__":
    main()


    











