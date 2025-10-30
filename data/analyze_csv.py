
"""
Script d'analyse des fichies CSV fournis.
Auteur: Jo Kabonga
Date : 30/10/2025
"""

import pandas as pd 
import os
import csv
from pathlib import Path


def analyze_csv_structure():
    """Analyser la structure des fichiers CSV """
    data_dir = Path(__file__).parent
    csv_files = list(data_dir.glob("*.csv")) # charger les fichiers .csv du dossier"data"
    print(f"Fichiers CSV trouvés: {len(csv_files)}")

    for csv_file in csv_files:
        print(f"\n FICHIER: {csv_file.name}")

        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                # Lecture de tout le fichier pour l'analyse
                lines = file.readlines() 
                print(f"Nombre total de lignes: {len(lines)}") 
                print(f" En-têtes: {lines[0].strip()}")

                #Afficher les premieres lignes de données
                print(f"\n Apercu du contenu: ")
                for i, line in enumerate(lines[1:5],2): #lignes 2,3,4,5
                    print(f"ligne {i}: {line.strip()[:100]}")

                # Analyser le séparateur
                first_line = lines[0]
                if ',' in first_line:
                    sep = ','
                elif ';' in first_line:
                    sep = ';'
                else:
                    sep = 'autre'
                print(f"Separateur détecté: '{sep}'")

                # compter les colonnes
                reader = csv.reader(lines, delimiter=sep)
                headers = next(reader)
                print(f"Nombre de colonnes: {len(headers)}")
                print(f"Colonnes: {headers}")

        except Exception as ex:
            print(f"Erreur: {ex}")

#End analyze_csv_structure


if __name__ == "__main__":
    analyze_csv_structure()
    