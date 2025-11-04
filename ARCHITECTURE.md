# Architecture Système - Recommandation de critiques
---

## Diagramme de l'Architecture
![System Design](docs/architecture.png)

---
## Modules Métier

### MODULE 1: Traitement des données
- Chargement des colonnes utiles (id,review_content,user_id)
- Nettoyage (NaN, textes vides, doublons)
- Ajout du film_id
- Export des données nettoyées

##### Générateur d'embeddings
- Modèle : SentenceTransformers (all-MiniLM-L6-v2)
- Transformation texte en vecteurs
- Traitement par lots

### MODULE 2: Stockage Vectoriel

##### Base Vectorielle
- Index séparé par film (fightclub, interstellar)

##### Stockage des Méta-données 
- Mapping vecteur en méta-données 
- Informations des critiques (id,user_id,film_id)
- Accès rapide . 

### MODULE 3: Recommandation


##### Logique métier principale
- récupération de l'embedding source
- recherche des similarités (même film dans notre cas)
- Filtrage des auto-recommandations 
- calcul des scores de similarités 
- Formatage des résultats (à étudier plus en détails)

### MODULE 4: API & Client


##### Serveur FastAPI
- Endpoint /recommendations
- validation des requêtes 
- gestion erreurs
- logging 
- documentation 

##### client sensCritique
- Intégration avec le frontend existant 
- appels API REST
- affichage des résultats 

---

## Flux de Données
![Diagramme sequence](docs/sequence.png)

---

## Choix Techniques

##### Module 1: Traitement des données
- **Langage**:Python 3.12
- **Modèle d'embedding**: all-MiniLM-L6-v2 (Sentence-BERT)
- **dimension**: 384 (performance/précision)
- **Stockage intermediaire**: NumPy et Pandas 

##### Module 2: Stockage Vectoriel
- **similarité**: cosinus (produit scalaire)
- **implémentation**: Sentence-Transformers 
- **Architecture de données**: séparation  par film
- **recherche**: linéaire Θ(n · d) pour 1000 critique apres nettoyage

##### Module 3: Moteur de recommandation
- **Filtrage**: auto-recommandation exclue
- **Seuillage**: similarité minimum configurable
- **Limitation**: nombre de résultats  (k) parametre.

##### Module 4: API (Pas demandé mais ...)

- **Framework**: FastAPI
- ** Validation**: Pydantic
- **Documentation** : Swagger auto-generée
- **Logging**: structure simple et informatif

## Evolutivité
- Architecture modulaire
- Chargement dynamique des films
- Données organisée par film

---
*Documenation technique - Test SensCritique*
