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

    def __init__(self):
        try:
            self.emb_films = {} # {film_id: vecteurs}
            self.dataF_emb_films = {} # {film_id: dataF des vecteurs}
            logger.info("stockage de vecteurs initialisé")
            
        except Exception as ex:
            logger.error(f"erreur de l'initialisation :{ex}")
            raise 
    #end __init__

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
            self.emb_films[film_id] = emb_films
            self.dataF_emb_films[film_id]= dataF_emb_films
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
            #verifier le film
            if film_id not in self.emb_films: #voir méthode add_film
                raise ValueError(f"film '{film_id}' non trouvé")
            #end if
            emb_films = self.emb_films[film_id] # on recup les vecteurs du film
            #calcul des similarités cosinus
            scores_similarity = util.cos_sim(vecteur_ref,emb_films)[0] # docs:

            #recup des k resultats
            scores_k, indices_k = scores_similarity.topk(k=min(k,len(scores_similarity)))

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
            #verifier le film_id
            if film_id not in self.dataF_emb_films:
                raise ValueError(f"film '{film_id}' non trouvé ")
            #end if
            return self.dataF_emb_films[film_id].iloc[indices].copy() # 
        except Exception as ex:
            logger.error(f"erreur recup métadonnées du film '{film_id}': {ex}")
            raise
    #end get_critique_metadata

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
        v_store =VectorStore()
        data_dir = Path("../../data/processed")

        #charg. fight club
        v_store.load_files(
            "interstellar",data_dir/"interstellar_avec_embeddings.npy",
            data_dir/ "interstellar_avec_embeddings.pkl"
        )
        #critique de ref
        critique_ref_index=30
        dataF_interstellar = v_store.dataF_emb_films["interstellar"]
        critique_ref = dataF_interstellar.iloc[critique_ref_index] # premiere critique
        print(f"critique de ref, index({critique_ref_index})")
        print(f"{critique_ref['review_content'][:200]}...")
        #print(f"note: {critique_ref['note']}")
        print(f"Film: {critique_ref['film_id']}")

        # critique similaire
        vecteur_ref = v_store.emb_films["interstellar"][critique_ref_index]
        scores, indices = v_store.search_similar_vectors("interstellar",vecteur_ref,k=10)

        print("10 critiques\n")
        compt =0
        user_id = [] #ajouter les user_id pour verifier 

        for i, (score, idx) in enumerate(zip(scores,indices)):
            if score !=1.0:
                compt +=1
                critique_sim = v_store.get_critique_metadata("interstellar",[idx]).iloc[0]
                print(f"Resultat numero {i+1}")
                print(f"similarité: {score:.4f}")
                print(f"index: {idx}")
                print(f"contenu : {critique_sim['review_content'][:200]}...")
                print(f" Film: {critique_sim['film_id']}")
                user_id.append(critique_sim['user_id'])
                print(f"User ID: {critique_sim['user_id']}")
            #end if 
            #verification
        #end for
        print(f"\n Total: {compt} critiques similaires (similarité >=0.8) | {user_id}")
    except Exception as ex:
        logger.error(f"erreur dans main: {ex}")
        raise
#end main

if __name__ == "__main__":
    main()


    











