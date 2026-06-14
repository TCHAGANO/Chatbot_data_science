# database.py
import streamlit as st
from sqlalchemy import create_engine
import urllib.parse

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "chatbot_db"
DB_USER = "postgres"
DB_PASS = "Bahiss@u02gnao"

@st.cache_resource
def initialiser_connexion():
    try:
        # 1. On protège le '@' du mot de passe
        password_encode = urllib.parse.quote_plus(DB_PASS)

        # 2. On crée l'URL propre avec le driver psycopg2
        connection_string = f"postgresql+psycopg2://{DB_USER}:{password_encode}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

        # 3. On génère le moteur SQLAlchemy
        engine = create_engine(connection_string, pool_pre_ping=True)
        return engine
    except Exception as e:
        st.error(f"❌ Erreur de connexion : {e}")
        return None