
"""
Lancement du serveur

Auteur: Jo kabonga
Date: 2/11/2025
"""

import uvicorn

if __name__ == "__main__":
    print("SensCritique api de recommandation")
    print("docs: htpps://localhost:8000/docs")
    print("Ctrl + C pour arreter\n")

    uvicorn.run(
        "src.api.main:app",
        host = "0.0.0.0",
        port = 8000,
        reload = True
    )
    