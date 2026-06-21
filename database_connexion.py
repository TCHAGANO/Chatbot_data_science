# database.py
import streamlit as st
from sqlalchemy import create_engine #  Creation du moteur de connexion SQLAlchemy à la base de données PostgreSQLbw
import urllib.parse # Encode les caractères spéciaux du mot de passe

# par exemple, si le mot de passe contient un '@', il faut l'encoder pour éviter les erreurs de connexion
# urllib.parse.quote_plus("Bahiss@u02gnao") donne comme résultat :
# Bahiss%40u02gnao comme ça PostgreSQL ne confondra pas le '@' du mot de passe avec le '@' de l'URL de connexion





# PostgreSQL est le serveur de bases de données.
# On peut le voir comme un immeuble contenant plusieurs bases de données.
# Ici nous allons nous connecter à la base nommée "chatbot_db".

DB_HOST = "localhost" #    PostgreSQL est installé sur la même machine que l'application
#  Localhost  signifie  exacement  que la base de données est sur la même machine que l'application, donc on peut utiliser "localhost" ou "

DB_PORT = "5432"  #  Port utilisé par PostgreSQL
DB_NAME = "chatbot_db"  #  Le  nom  de la base de données que nous allons utiliser pour stocker les données du chatbot
DB_USER = "postgres"  #  Le nom d'utilisateur pour se connecter à la base de données
DB_PASS = "Bahiss@u02gnao"  #  Le  mot de passe pour se connecter à la base de données

@st.cache_resource #  Pour garder la connexion PostgreSQL en mémoire pour éviter de la recréer à chaque exécution

 # Fonction qui crée et retourne une connexion PostgreSQL
def initialiser_connexion():   
    try: 
        # 1. On protège le '@' du mot de passe
        password_encode = urllib.parse.quote_plus(DB_PASS)

        # 2. On crée l'URL propre avec le driver psycopg2
        # Construction de l'URL complète de connexion :
        # utilisateur + mot de passe + serveur + port + base de données
        connection_string = f"postgresql+psycopg2://{DB_USER}:{password_encode}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
 
        # 3. On génère le moteur SQLAlchemy 
        #   Cette voiture s'appelle engine, c'est elle qui va nous permettre 
        # de nous connecter à la base de données PostgreSQL
        # Vérifie que la connexion est toujours active avant utilisation.
        # Si la connexion est cassée ou fermée,
        # SQLAlchemy en crée automatiquement une nouvelle.
        engine = create_engine(connection_string, pool_pre_ping=True)
        return engine  # Retourne le moteur SQLAlchemy permettant d'accéder à PostgreSQL
    
    #  Gestion des  erreurs  :  si mot de passe  ou Postgree arrêté ou mauvais port ..
    #  Au  lieu que le programme plante, on affiche un message d'erreur à l'utilisateur et on retourne None
    except Exception as e:
        st.error(f"❌ Erreur de connexion : {e}")
        return None