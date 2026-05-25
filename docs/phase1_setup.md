# PHASE 1 — Setup du projet

## Date

23/05/2026

---

## Objectif

Préparer l’environnement de travail et générer les données du projet chatbot.

---

## Actions réalisées

### 1. Installation des bibliothèques

Commande utilisée :

```bash
pip install pandas numpy faker sqlalchemy psycopg2 streamlit
```

Bibliothèques installées :

- pandas → manipulation données CSV
- numpy → calculs numériques
- faker → génération données fictives
- sqlalchemy → connexion Python ↔ SQL
- psycopg2 → communication PostgreSQL
- streamlit → création interface web

---

### 2. Création du fichier de génération

Fichier créé :

generate_chatbot_data.py
J'ai utiliser deepseek pour générer ces données.  
taille : 500 000
Objectif :

Générer un dataset simulé contenant :

- clients
- produits
- magasins
- fournisseurs
- ventes
- commandes
- En suite créér un chatbot interactif
---

### 3. Génération du CSV

Commande :

```bash
python generate_chatbot_data.py
```

Résultat :

chatbot_data.csv généré.

---

### 4. Création environnement virtuel

Commande :

```bash
python -m venv venv
```

Pourquoi ?

Créer un environnement Python spécifique au projet afin d’éviter les conflits entre bibliothèques.

---

## Ce que j'ai appris

- créer un projet structuré
- générer un dataset automatiquement
- utiliser Faker
- créer un environnement virtuel


---

## Difficultés rencontrées

Pas de difficulté majeure 

---

## Solutions

Ce n'est pas encore chaud pour l'instant

---

## Prochaine étape

-Analyser le dataset généré.
-comprendre ce  qu'il y'a dans notre fichier

# ##########################
 Dans le cas oû les données sont réelles, alors  il est important de chercher  à comprendre :

-combien de lignes il y'a
-quelles colonnes existent
-les types des données
-s’il y a des valeurs manquantes
-les relations entre les données
# #########################
