
"""Test generés par l'IA pour le module data_cleaner.py en utilisant de vrais fichiers CSV situés dans le dossier data/."""
import pytest
import pandas as pd
import sys
from pathlib import Path

# Ajouter 'src' au PYTHONPATH pour pouvoir importer le package sous src/
sys.path.insert(0, str((Path(__file__).resolve().parents[1] / "src")))

from data_processing.data_cleaner  import clean_critiques_data, validate_cleaned_data, save_cleaned_data

class TestDataCleanerWithRealFiles:
    """Tests avec les fichiers CSV réels"""
    
    def test_clean_critiques_data_with_fightclub(self):
        """Test du nettoyage avec le vrai fichier Fight Club"""
        # Arrange
        csv_path = Path(__file__).parent.parent / "data" / "fightclub_critiques.csv"
        
        # Act
        result = clean_critiques_data(csv_path, "fightclub")
        
        # Assert
        assert len(result) > 0
        assert 'film_id' in result.columns
        assert 'review_content' in result.columns
        assert 'user_id' in result.columns
        assert result['film_id'].iloc[0] == "fightclub"
        
        # Vérifier qu'il n'y a pas de valeurs manquantes dans review_content
        assert result['review_content'].isna().sum() == 0
        assert (result['review_content'].str.strip() == '').sum() == 0
        
        print(f"✅ Fight Club: {len(result)} critiques nettoyées")
    
    def test_clean_critiques_data_with_interstellar(self):
        """Test du nettoyage avec le vrai fichier Interstellar"""
        # Arrange
        csv_path = Path(__file__).parent.parent / "data" / "interstellar_critique.csv"
        
        # Act
        result = clean_critiques_data(csv_path, "interstellar")
        
        # Assert
        assert len(result) > 0
        assert 'film_id' in result.columns
        assert 'review_content' in result.columns
        assert 'user_id' in result.columns
        assert result['film_id'].iloc[0] == "interstellar"
        
        # Vérifier la qualité des données nettoyées
        assert result['review_content'].isna().sum() == 0
        assert (result['review_content'].str.strip() == '').sum() == 0
        
        print(f"✅ Interstellar: {len(result)} critiques nettoyées")
    
    def test_validate_cleaned_data_with_real_data(self):
        """Test de validation avec les données réelles nettoyées"""
        # Arrange
        fightclub_data = clean_critiques_data(Path(__file__).parent.parent / "data" / "fightclub_critiques.csv", "fightclub")
        interstellar_data = clean_critiques_data(Path(__file__).parent.parent / "data" / "interstellar_critique.csv", "interstellar")
        
        # Act & Assert
        assert validate_cleaned_data(fightclub_data, "fightclub") == True
        assert validate_cleaned_data(interstellar_data, "interstellar") == True
        
        print("✅ Validation des données réelles réussie")
    
    def test_validate_cleaned_data_fails_with_invalid_data(self):
        """Test que la validation échoue avec des données invalides"""
        # Arrange - DataFrame sans la colonne requise
        invalid_df = pd.DataFrame({
            'id': [1, 2],
            'user_id': ['user1', 'user2']
            # Manque 'review_content' et 'film_id'
        })
        
        # Act & Assert
        with pytest.raises(ValueError, match="Colonne manquante"):
            validate_cleaned_data(invalid_df, "test_movie")
        
        print("✅ Test d'échec de validation réussi")
    
    def test_save_cleaned_data_with_real_data(self):
        """Test de sauvegarde avec les données réelles"""
        # Arrange
        fightclub_data = clean_critiques_data(Path(__file__).parent.parent / "data" / "fightclub_critiques.csv", "fightclub")
        output_dir = Path(__file__).parent.parent / "data" / "test_output"
        
        # Act
        save_path = save_cleaned_data(fightclub_data, "fightclub_test", output_dir)
        
        # Assert
        assert save_path.exists()
        
        # Vérifier que le fichier sauvegardé peut être relu
        saved_data = pd.read_csv(save_path)
        assert len(saved_data) == len(fightclub_data)
        assert 'review_content' in saved_data.columns
        
        # Nettoyer le fichier de test
        save_path.unlink()
        
        print(f"✅ Sauvegarde réussie: {save_path}")
    
    def test_complete_workflow(self):
        """Test du workflow complet avec les vrais fichiers"""
        # Arrange
        films = [
            (Path(__file__).parent.parent / "data" / "fightclub_critiques.csv", "fightclub"),
            (Path(__file__).parent.parent / "data" / "interstellar_critique.csv", "interstellar")
        ]
        
        for csv_path, film_name in films:
            # Act - Nettoyage
            cleaned_data = clean_critiques_data(csv_path, film_name)
            
            # Assert - Validation
            assert validate_cleaned_data(cleaned_data, film_name) == True
            
            # Act - Sauvegarde
            save_path = save_cleaned_data(cleaned_data, f"{film_name}_workflow_test", Path(__file__).parent.parent / "data" / "test_output")
            
            # Assert - Vérification de la sauvegarde
            assert save_path.exists()
            
            # Nettoyer
            save_path.unlink()
            
            print(f"✅ Workflow complet réussi pour {film_name}")

def test_data_quality_after_cleaning():
    """Test de la qualité des données après nettoyage"""
    # Arrange & Act
    fightclub_clean = clean_critiques_data(Path(__file__).parent.parent / "data" / "fightclub_critiques.csv", "fightclub")
    interstellar_clean = clean_critiques_data(Path(__file__).parent.parent / "data" / "interstellar_critique.csv", "interstellar")
    
    # Assert - Vérifications de qualité
    for df, name in [(fightclub_clean, "Fight Club"), (interstellar_clean, "Interstellar")]:
        # Pas de valeurs manquantes dans les colonnes critiques
        assert df['review_content'].isna().sum() == 0, f"Valeurs manquantes dans review_content pour {name}"
        assert df['film_id'].isna().sum() == 0, f"Valeurs manquantes dans film_id pour {name}"
        
        # Pas de textes vides
        empty_texts = (df['review_content'].str.strip() == '').sum()
        assert empty_texts == 0, f"Textes vides trouvés pour {name}: {empty_texts}"
        
        # user_id tous remplis (soit valeur originale, soit 'anonyme')
        assert df['user_id'].isna().sum() == 0, f"User_id manquants pour {name}"
        
        # Vérifier que film_id est correctement assigné
        unique_films = df['film_id'].unique()
        assert len(unique_films) == 1, f"Multiple film_id pour {name}: {unique_films}"
        
        print(f"✅ Qualité données vérifiée pour {name}: {len(df)} lignes")

if __name__ == "__main__":
    print("🚀 LANCEMENT DES TESTS AVEC FICHIERS RÉELS")
    print("=" * 50)
    
    # Créer une instance de la classe de test
    test_instance = TestDataCleanerWithRealFiles()
    
    # Exécuter les tests un par un
    try:
        test_instance.test_clean_critiques_data_with_fightclub()
        test_instance.test_clean_critiques_data_with_interstellar()
        test_instance.test_validate_cleaned_data_with_real_data()
        test_instance.test_validate_cleaned_data_fails_with_invalid_data()
        test_instance.test_save_cleaned_data_with_real_data()
        test_instance.test_complete_workflow()
        test_data_quality_after_cleaning()
        
        print("=" * 50)
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        
    except Exception as e:
        print(f"❌ TEST ÉCHOUÉ: {e}")
        raise
