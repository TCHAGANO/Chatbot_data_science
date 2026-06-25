import streamlit as st
from sqlalchemy import create_engine #  Creation du moteur de connexion SQLAlchemy à la base de données PostgreSQLbw
import urllib.parse # Encode les caractères spéciaux du mot de passe

# par exemple, si le mot de passe contient un '@', il faut l'encoder pour éviter les erreurs de connexion
# urllib.parse.quote_plus("Bahiss@u02gnao") donne comme résultat :
# Bahiss%40u02gnao comme ça PostgreSQL ne confondra pas le '@' du mot de passe avec le '@' de l'URL de connexion

DB_HOST = "localhost" #    PostgreSQL est installé sur la même machine que l'application
DB_PORT = "5432"  #  Port utilisé par PostgreSQL
DB_NAME = "chatbot_db"  #  Le  nom  de la base de données que nous allons utiliser pour stocker les données du chatbot
DB_USER = "postgres"  #  Le nom d'utilisateur pour se connecter à la base de données
DB_PASS = "Bahiss@u02gnao"  #  Le  mot de passe pour se connecter à la base de données

@st.cache_resource #  Pour garder la connexion PostgreSQL en mémoire pour éviter de la recréer à chaque exécution
def initialiser_connexion():   
    try: 
        # 1. DISPOSITIF AUTOMATIQUE : Est-ce qu'on est en ligne sur Streamlit Cloud ?
        if "postgres" in st.secrets:
            # On récupère directement le lien Neon que tu as enregistré dans les Secrets
            connection_string = st.secrets["postgres"]["DATABASE_URL"]
        
        # 2. SINON : On utilise ta configuration locale de ton PC (localhost)
        else:
            password_encode = urllib.parse.quote_plus(DB_PASS)
            connection_string = f"postgresql+psycopg2://{DB_USER}:{password_encode}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
 
        # S'assurer que le lien commence bien par "postgresql://" ou "postgresql+psycopg2://"
        if connection_string.startswith("postgres://"):
            connection_string = connection_string.replace("postgres://", "postgresql://", 1)

        # 3. On génère le moteur SQLAlchemy
        engine = create_engine(connection_string, pool_pre_ping=True)
        return engine  # Retourne le moteur SQLAlchemy permettant d'accéder à PostgreSQL
    
    except Exception as e:
        st.error(f"❌ Erreur de connexion : {e}")
        return None