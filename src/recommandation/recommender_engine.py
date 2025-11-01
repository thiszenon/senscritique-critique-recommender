"""
Ici, on gere le moteur de recommandation
Auteur: Jo kabonga
Date: 1/11/2025

"""

import pandas as pd
import logging
import sys
from typing import Optional
from pathlib import Path

#Config du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s- %(message)s'
)
logger = logging.getLogger(__name__)

class RecommanderEngine:
    """
    Moteur de recommandation de critiques similaires
    TODO: optimise au max si possible .
    Comment le moteur a été pensé:
        - lier les IDS de critiques aux index numériques
        - orchestre la recherche de similarités
        - filtrer et formater les resultats
        - Et si le temps le permet , optimisation
    """
    def __init__(self, vector_store):
        """
        Initialisation avec la class VectorStore
        Args:
            vector_store: Instance de VectoreStore (module 2)
        """
        try:
            self.vectore_store = vector_store
            logger.info("RecommenderEngine initialisé...")
        except Exception as ex:
            logger.error(f"erreur initialisation: {ex}")
            raise
    #end __init__

    def _get_index_with_id(self,film_id:str, critque_id:str) -> Optional[int]:
        """
        Trouver l'index d'une critique à partir de son ID
        Args:
            film_id: ID du film
            critque_id: ID de la critique (doit etre unique!!!)
        Returns:
            index numerique ou None si pas trouvé
        """
        try:
            #verifier que le film existe ou pas
            if film_id not in self.vectore_store.dataF_emb_films:
                logger.error(f"Film '{film_id}' non trouvé")
                return None
            #end if
            dataF = self.vectore_store.dataF_emb_films[film_id] # recuperer le film_id du dataF
            
            #conversion de l'ID en int (structure du dataF...)
            try:
                critique_id_int = int(critque_id)
            except ValueError:
                logger.error(f"ID de la critique invalide: {critque_id}")
                return None
            
            #recherche la critique par ID
            result =  dataF['id'] == critique_id_int
            if not result.any():
                logger.error(f"critique ID {critque_id} non trouvé , ref :{film_id}")
                return None
            #end if

            index_trouver = dataF[result].index[0]
            logger.info(f"critique {critque_id} -> index {index_trouver}")
            return index_trouver
        except Exception as ex:
            logger.error(f"erreur recherche critique {critque_id}: {ex}")
            return None
        
    #end _get_index_with_id

    def find_similar(self, critique_id:str, film_id:str, k:int ,scores_sim_min:float =0.8) -> pd.DataFrame:
        """
        Trouver les critiques similaires à une critique donnée

        Args:
            critique_id: ID de la critique pour laquelle la recherche sera effectuée
            film_id: film dans lequel rechercher
            k: nombre de résultats max
            scores_sim_min: seuil min de similarité 

        Returns:
            DataFrame des critiques similaires avec des scores de similarité (à revoir)

        """
        try:
            logger.info(f"recherche similarité : critique={critique_id}, film={film_id}")

            # Trouver l'index de la critique de ref
            index_ref = self._get_index_with_id(film_id,critique_id)
            if index_ref is None:
                raise ValueError(f"critique {critique_id} inexistante pour le film {film_id}")
            #end if

            # Recuperer le vecteur de l'index_ref
            vecteur_ref = self.vectore_store.emb_films[film_id][index_ref]
            logger.info(f"vecteur de ref récupérer (index {index_ref})")

            #rechercher les critiques similaires 
            scores, indices = self.vectore_store.search_similar_vectors(film_id,vecteur_ref,k)
            logger.info(f"{len(scores)} similarités trouvées ...")

            # filtrer auto recommandation critique_ref
            masque_auto = indices != index_ref 
            scores_filtres = scores[masque_auto] # que les sim sans la critique de ref
            indices_filtres = indices[masque_auto] 

            # verifier l'auto recommandation
            if len(scores_filtres) < len(scores):
                logger.info("auto recommandation reussi")
            #end if

            # Filtre par seuil de similarité 
            masque_seuil = scores_filtres >= scores_sim_min
            scores_finals = scores_filtres[masque_seuil]
            indices_finales = indices_filtres[masque_seuil] # que les indices dans le seuil de similarité

            # verifier le nombre apres le filtre
            nb_filtre_seuil = len(scores_filtres) - len(scores_finals)
            if nb_filtre_seuil > 0:
                logger.info(f"{nb_filtre_seuil} results filtrés pour le seuil {scores_sim_min}")
            #end if

            # Limiter au nombre demandé ou revoir vector_store 
            scores_final = scores_finals[:k] 
            indices_finale = indices_finales[:k]
            if len(scores_final) == 0:
                logger.warning("pas de critiques similaires trouvee apres le filtre")
                return pd.DataFrame()
            #end if

            # recuperer les metadata
            critiques_similaires = self.vectore_store.get_critique_metadata(film_id,indices_finale)

            # ajout des scores de similarités au dataF
            critiques_similaires['similarity_score'] = scores_final
            logger.info(f"{len(critiques_similaires)} critiques similaires trouvées")

            return critiques_similaires
        except Exception as ex:
            logger.error(f"erreur recherche de similarités: {ex}")
            raise
    #end find_similar

# main
def main():
    try:
        logger.info("Main recommandation")
        #import de la classe VectorStore
        sys.path.append(str(Path(__file__).parent.parent))
        from vector_store.vector_store import VectorStore
        vector_store = VectorStore() 

        # les données
        data_dir = "../../data/processed"
        vector_store.load_files("fightclub",f"{data_dir}/fightclub_avec_embeddings.npy",f"{data_dir}/fightclub_avec_embeddings.pkl")

        # Initialiser le moteur de recommandation
        engine_R = RecommanderEngine(vector_store)

        # ID critique pour tester
        dataF_fightclub = vector_store.dataF_emb_films["fightclub"]
        critique_id_test = str(dataF_fightclub['id'].iloc[132]) # la critique 1

        print(f"Test avec critique ID: {critique_id_test}")
        print(f"\n La critique de ref: {dataF_fightclub['review_content'].iloc[132][:300]}... ")
        print("\n")

        # la recherche
        resultats = engine_R.find_similar(
            critique_id=critique_id_test,
            film_id="fightclub", #tester autre nom
            k=10,
            scores_sim_min=0.8# seuil de test à definir pour la production 
        )

        # Afficher les resultats
        if len(resultats) > 0:
            print(f"{len(resultats)} Critiques similaires trouvés:")
            for i, (index,row) in enumerate(resultats.iterrows()):
                print(f"\n {i+1} (similarité: {row['similarity_score']:.4f})")
                print(f" User: {row['user_id']}")
                print(f"Critique: {row['review_content'][:300]}...")
            #end for
        else:
            print("aucun résultat trouvé")
        return engine_R
    except Exception as ex:
        logger.error(f"erreur : {ex}")
        raise
#end main

if __name__ == "__main__":
    main()
