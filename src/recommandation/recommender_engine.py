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
            self.vector_store = vector_store
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
            film_data = self.vector_store.load_film(film_id)
            dataF_metadata = film_data['metadata']

            #conversion de l'ID en int
            try:
                critique_id_int = int(critque_id)
            except ValueError:
                logger.error(f"ID de la critique invalide: {critque_id}")
                return None
            
            #recherche la critique par ID
            masque = dataF_metadata['id'] == critique_id_int
            if not masque.any():
                logger.error(f"critique ID {critque_id} non trouvée pour le film {film_id}")
                return None
            #end if
            index_trouver = dataF_metadata[masque].index[0]
            logger.info(f"critique {critque_id} -> index {index_trouver}")
            return index_trouver
        except Exception as ex:
            logger.error(f"erreur rcherche critique {critque_id}: {ex}")
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

            #verifier que le film existe
            if not self.vector_store.film_exists(film_id):
                raise ValueError(f"film '{film_id}' non dispo")
            #end if


            # Trouver l'index de la critique de ref
            index_ref = self._get_index_with_id(film_id,critique_id)
            if index_ref is None:
                raise ValueError(f"critique {critique_id} inexistante pour le film {film_id}")
            #end if

            film_data = self.vector_store.load_film(film_id)
            vecteur_ref = film_data['embeddings'][index_ref]

            logger.info(f"vecteur de ref recupérer (index {index_ref})")

            #rechercher les critiques similaires 
            scores, indices = self.vector_store.search_similar_vectors(film_id,vecteur_ref,k+1)
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
            critiques_similaires = self.vector_store.get_critique_metadata(film_id,indices_finale)

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
        
        # Initialiser le moteur de recommandation
        engine_R = RecommanderEngine(vector_store)

        #verifier les films dispo
        films = vector_store.list_available_films()
        print(f"films dipo: {films}")

        film_test = "interstellar"
        if film_test not in films:
            print(f"film '{film_test}' non disponible")
            return
        #end if
        
        film_data = vector_store.load_film(film_test)
        dataF_metadata = film_data['metadata']

        #ID critique pour tester
        critique_id_test = str(dataF_metadata['id'].iloc[132])

        print(f"Test avec critique ID: {critique_id_test}")
        print(f"\n La critique de ref: {dataF_metadata['review_content'].iloc[132][:300]}... ")
        print("\n")

        # la recherche
        resultats = engine_R.find_similar(
            critique_id=critique_id_test,
            film_id=film_test, #tester autre nom
            k=5, # pour le teste
            scores_sim_min=0.7# seuil de test à definir pour la production 
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
