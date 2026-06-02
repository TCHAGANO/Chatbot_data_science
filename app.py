# app.py

import streamlit as st
import pandas as pd
import os
import base64
import time

# Importation de nos modules métiers (Séparation des responsabilités)
from database import initialiser_connexion
from llm import generer_requete_sql

# --- CONFIGURATION INTERFACE & LOOK LIGHT MODE PREMIUM ---
st.set_page_config(page_title="Assistant IA - Business Intelligence", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
        /* Fond global blanc/gris clair de l'application */
        .stApp { background-color: #F8FAFC !important; color: #1E293B !important; }
        
        /* Sidebar blanche épurée */
        section[data-testid="stSidebar"] { 
            background-color: #FFFFFF !important; 
            border-right: 1px solid #E2E8F0 !important; 
        }
        
        /* Style des cartes de suggestion Bento (Style Pastel) */
        .bento-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 20px;
            min-height: 140px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            transition: all 0.2s ease-in-out;
            position: relative;
            overflow: hidden;
        }
        .bento-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
            border-color: #CBD5E1;
        }
        
        /* Petite barre colorée en haut de chaque carte */
        .bento-card::before {
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0; height: 4px;
        }
        .card-green::before { background: linear-gradient(90deg, #4ADE80, #22C55E); }
        .card-blue::before { background: linear-gradient(90deg, #60A5FA, #3B82F6); }
        .card-purple::before { background: linear-gradient(90deg, #C084FC, #A855F7); }
        .card-orange::before { background: linear-gradient(90deg, #FB923C, #F97316); }

        .bento-title {
            font-size: 15px;
            font-weight: 600;
            margin-bottom: 6px;
        }
        .title-green { color: #166534; }
        .title-blue { color: #1E40AF; }
        .title-purple { color: #6B21A8; }
        .title-orange { color: #9A3412; }
        
        .bento-desc { color: #64748B; font-size: 13px; line-height: 1.4; }
        
        /* Titre central */
        .hero-title {
            font-size: 32px;
            font-weight: 700;
            color: #0F172A;
            text-align: center;
            margin-top: 20px;
        }
        
        /* Photo de profil agrandie et valorisée en haut à droite */
        .top-profile-pic {
            border-radius: 50%;
            border: 2px solid #3B82F6;
            width: 60px;
            height: 60px;
            object-fit: cover;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }
        
        /* Input de chat style épuré */
        div[data-baseweb="input"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 14px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        }
        div[data-baseweb="input"]:focus-within {
            border-color: #3B82F6 !important;
        }
        
        #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Initialisation de la connexion de la base de données
engine = initialiser_connexion()

# --- GESTION DES ÉTATS DE SESSION (MÉMOIRE) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "application_active" not in st.session_state:
    st.session_state.application_active = True

# --- BANDEAU SUPÉRIEUR (TOP BAR) ---
top_col1, top_col2, top_col3 = st.columns([3, 4, 1])

with top_col1:
    st.markdown("<div style='background: #FFFFFF; padding: 8px 16px; border-radius: 10px; border: 1px solid #E2E8F0; font-size: 13px; font-weight: 500; display: inline-block; color: #475569;'>🤖 Mistral AI 7B (Local Node)</div>", unsafe_allow_html=True)

with top_col3:
    if os.path.exists("ma_photo.jpeg"):
        with open("ma_photo.jpeg", "rb") as img_file:
            encoded_img = base64.b64encode(img_file.read()).decode()
        st.markdown(f"<div style='text-align: right; margin-top: -10px;'><img src='data:image/jpeg;base64,{encoded_img}' class='top-profile-pic'></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align: right; font-size: 28px;'>👤</div>", unsafe_allow_html=True)

# --- ACCUEIL BIENVENUE & BENTO GRID ---
if len(st.session_state.messages) == 0:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #3B82F6; font-weight: 600; margin-bottom: 0; font-size:14px;'>Welcome to BI Chatbot Pro</p>", unsafe_allow_html=True)
    st.markdown("<h1 class='hero-title' style='margin-top: 0;'>How Can I Assist You Today?</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    card_col1, card_col2, card_col3, card_col4 = st.columns(4)

    with card_col1:
        st.markdown("""
            <div class="bento-card card-green">
                <div class="bento-title title-green">📊 Volume Global</div>
                <div class="bento-desc">Déterminez le nombre exact de clients ou de commandes dans la base.</div>
            </div>
        """, unsafe_allow_html=True)

    with card_col2:
        st.markdown("""
            <div class="bento-card card-blue">
                <div class="bento-title title-blue">🏆 Top Performances</div>
                <div class="bento-desc">Trouvez instantanément la référence produit ou la marque la plus vendue.</div>
            </div>
        """, unsafe_allow_html=True)

    with card_col3:
        st.markdown("""
            <div class="bento-card card-purple">
                <div class="bento-title title-purple">🎯 Profils Clients</div>
                <div class="bento-desc">Analysez la répartition de vos acheteurs par ville, âge ou par sexe.</div>
            </div>
        """, unsafe_allow_html=True)

    with card_col4:
        st.markdown("""
            <div class="bento-card card-orange">
                <div class="bento-title title-orange">💸 Analyse CA & Marge</div>
                <div class="bento-desc">Calculez les profits générés et observez l'impact des remises accordées.</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><hr style='border-color: #E2E8F0;'><br>", unsafe_allow_html=True)

# --- BARRE LATÉRALE GAUCHE ---
with st.sidebar:
    st.markdown("<h3 style='color: #0F172A; font-size: 18px; font-weight:700; margin-bottom:0;'>📁 Aplot AI BI</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 13px; margin-top:0;'>Bahissou TCHAGNAO</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    if st.button("🆕 New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.application_active = True
        st.rerun()
        
    if st.button("🚪 Export & Quit", use_container_width=True):
        st.session_state.application_active = False
        st.rerun()

    st.markdown("<br>" * 4, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<p style='color:#64748B; font-size:12px; margin-bottom:15px;'><b>Spécifications Techniques :</b><br>• PostgreSQL (500k Records)<br>• Mistral-7B LLM Engine<br>• Pipeline Text-to-SQL Structuré</p>", unsafe_allow_html=True)
    
    # Intégration de tes réseaux professionnels réels
    st.link_button("💼 Profil LinkedIn", "https://www.linkedin.com/in/bahissou-tchagnao-9a91492aa", use_container_width=True)
    st.link_button("💻 Repository GitHub", "https://github.com/TCHAGANO/Chatbot_data_science.git", use_container_width=True)

# --- RECONSTRUCTION DE L'HISTORIQUE DES MESSAGES ---
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            if msg.get("is_sql", True) and msg.get("df_resultat") is not None:
                tab1, tab2, tab3 = st.tabs(["📊 Résultat", "🗄 SQL", "🤖 IA"])
                with tab1:
                    df = msg["df_resultat"]
                    if df.shape == (1, 1):
                        st.metric(label="Indicateur Unique", value=df.iloc[0, 0])
                    else:
                        st.dataframe(df, use_container_width=True)
                with tab2:
                    st.code(msg["query_sql"], language="sql")
                with tab3:
                    st.info(msg["analytics_text"])
            else:
                st.markdown(msg["content"])

# --- ZONE DE CAPTURE DE LA SAISIE (STRUCTURES NETTOYÉES) ---
if st.session_state.application_active:
    st.markdown("""
        <div style='display: flex; gap: 8px; margin-bottom: -10px; justify-content: center;'>
            <span style='background: #E2E8F0; color: #475569; font-size: 11px; padding: 4px 12px; border-radius: 20px; font-weight: 500;'>⚡ Fast Mode</span>
            <span style='background: #E2E8F0; color: #475569; font-size: 11px; padding: 4px 12px; border-radius: 20px; font-weight: 500;'>🔍 Deep SQL Check</span>
            <span style='background: #E2E8F0; color: #475569; font-size: 11px; padding: 4px 12px; border-radius: 20px; font-weight: 500;'>📊 Auto-Charts</span>
        </div>
    """, unsafe_allow_html=True)

    question_utilisateur = st.chat_input("Initiate a query or send a command to the AI...")

    if question_utilisateur:
        st.session_state.messages.append({"role": "user", "content": question_utilisateur})
        st.rerun()

# --- PIPELINE DE TRAITEMENT BACKEND & PIPELINE DE SÉCURITÉ ---
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and st.session_state.application_active:
    with st.chat_message("assistant"):
        with st.spinner("🤖 Réflexion de l'assistant en cours..."):
            try:
                debut_llm = time.time()
                reponse_ia = generer_requete_sql(st.session_state.messages)
                fin_llm = time.time()

                if "SELECT" in reponse_ia.upper():
                    requete_sql = reponse_ia
                    if "LIMIT" not in requete_sql.upper():
                        requete_sql = requete_sql.rstrip('; ') + " LIMIT 100;"

                    debut_sql = time.time()
                    df_resultat = pd.read_sql(requete_sql, engine)
                    fin_sql = time.time()

                    txt_performance = f"Génération SQL : {round(fin_llm - debut_llm, 2)}s | Base de données : {round(fin_sql - debut_sql, 2)}s."
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "Résultat extrait avec succès.",
                        "is_sql": True,
                        "df_resultat": df_resultat,
                        "query_sql": requete_sql,
                        "analytics_text": txt_performance
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": reponse_ia,
                        "is_sql": False,
                        "df_resultat": None,
                        "query_sql": None,
                        "analytics_text": "Analyse conversationnelle directe."
                    })
                st.rerun()
                
            except Exception as e:
                # Interception gracieuse de l'erreur pour garder une UI propre
                message_propre = "⚠️ Veuillez reformuler votre question ou poser une autre question."
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": message_propre,
                    "is_sql": False,
                    "df_resultat": None,
                    "query_sql": None,
                    "analytics_text": f"Erreur système interceptée : {e}"
                })
                st.rerun()