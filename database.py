# database.py

import streamlit as st
import urllib.parse
from sqlalchemy import create_engine

@st.cache_resource
def initialiser_connexion():
    """Crée et met en cache la connexion vers PostgreSQL."""
    password = urllib.parse.quote_plus("Bahiss@u02gnao")
    return create_engine(f"postgresql://postgres:{password}@localhost:5432/chatbot_db")