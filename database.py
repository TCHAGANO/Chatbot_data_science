# database.py
# Fichier situé à la racine : C:\Users\Bahissou TCHAGNAO\Desktop\Chatbot_project\Chatbot_data_science\database.py

import streamlit as st
from sqlalchemy import create_engine
import psycopg2
import urllib.parse  # Permet d'encoder proprement le caractère '@' du mot de passe

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "chatbot_db"
DB_USER = "postgres"
DB_PASS = "Bahiss@u02gnao"

@st.cache_resource
def initialiser_connexion():
    try:
        # Encodage sécurisé du mot de passe pour éviter le conflit avec le caractère '@'
        password_encode = urllib.parse.quote_plus(DB_PASS)

        # Construction de la chaîne de connexion avec le mot de passe sécurisé
        connection_string = (
            f"postgresql+psycopg2://"
            f"{DB_USER}:{password_encode}@"
            f"{DB_HOST}:{DB_PORT}/"
            f"{DB_NAME}"
        )

        engine = create_engine(
            connection_string,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )

        # Test de validation de la connexion
        with engine.connect():
            pass

        return engine

    except Exception as e:
        st.error(
            f"❌ Erreur PostgreSQL : {e}"
        )
        return None