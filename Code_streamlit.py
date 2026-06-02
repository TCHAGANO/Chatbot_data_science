import streamlit as st
import ollama
import pandas as pd
from sqlalchemy import create_engine
import urllib.parse
import os
import base64
import time

# 1. Configuration de la page Web
st.set_page_config(page_title="Assistant IA - Business Intelligence", page_icon="🤖", layout="wide")

# --- INJECTION CSS ---
st.markdown("""
    <style>
        .stApp { background-color: #0B0E14 !important; color: #E2E8F0 !important; }
        section[data-testid="stSidebar"] { background-color: #06080C !important; border-right: 1px solid #1E293B !important; }
        div[data-baseweb="input"] { background-color: #111827 !important; border: 2px solid #1F2937 !important; border-radius: 24px !important; color: #FFFFFF !important; padding: 4px 12px; }
        div[data-baseweb="input"]:focus-within { border-color: #3B82F6 !important; box-shadow: 0 0 10px rgba(59, 130, 246, 0.5) !important; }
        .suggestion-box { background-color: #111827; border: 1px solid #1F2937; border-radius: 12px; padding: 15px; text-align: left; min-height: 80px; color: #9CA3AF; font-size: 14px; }
        .suggestion-box strong { color: #E5E7EB; display: block; margin-bottom: 4px; }
        #MainMenu, footer, header {visibility: hidden;}
        .profile-pic { border-radius: 50%; border: 3px solid #3B82F6; display: block; margin-left: auto; margin-right: auto; width: 120px; height: 120px; object-fit: cover; }
        .kpi-container { background-color: #111827; border: 1px solid #3B82F6; padding: 20px; border-radius: 12px; text-align: center; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

# 2. Connexion PostgreSQL
@st.cache_resource
def initialiser_connexion():
    password = urllib.parse.quote_plus("Bahiss@u02gnao")
    return create_engine(f"postgresql://postgres:{password}@localhost:5432/chatbot_db")

engine = initialiser_connexion()

# --- BARRE LATÉRALE GAUCHE ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    
    if os.path.exists("ma_photo.jpeg"):
        with open("ma_photo.jpeg", "rb") as img_file:
            encoded_img = base64.b64encode(img_file.read()).decode()
        st.markdown(f'<img src="data:image/jpeg;base64,{encoded_img}" class="profile-pic">', unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align:center; color:#6B7280; padding:20px; border:1px dashed #1E293B; border-radius:50%; width:120px; height:120px; margin:auto;'>[Photo]</div>", unsafe_allow_html=True)
        
    st.markdown("<h3 style='text-align: center; color: white; margin-bottom:0;'>Bahissou TCHAGNAO</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #3B82F6; font-size:14px; margin-top:0;'>Étudiant en Data Science</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📂 Spécifications du Système")
    st.markdown("• **Database :** PostgreSQL (500k lignes)")
    st.markdown("• **Engine :** Text-to-SQL Pipeline")
    st.markdown("• **LLM :** Mistral AI")

    st.markdown("---")
    st.markdown("<p style='color:#3B82F6; font-size:12px; font-weight:bold; text-transform:uppercase;'>🚀 OPPORTUNITÉ</p>", unsafe_allow_html=True)
    st.markdown("""
        <div style="background-color: #111827; border-left: 4px solid #3B82F6; padding: 10px; border-radius: 4px; margin-bottom: 15px;">
            <p style="margin: 0; font-size: 13px; color: #E2E8F0;">
                🎯 <b>En recherche de stage</b><br>
                <span style="font-size: 11px; color: #9CA3AF;">Disponible immédiatement (3-6 mois)</span>
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.link_button("💼 Mon Profil LinkedIn", "https://www.linkedin.com/in/bahissou-tchagnao-9a91492aa", use_container_width=True)
    st.link_button("💻 Mon Portfolio GitHub", "https://github.com/TCHAGANO/Chatbot_data_science", use_container_width=True)

# 3. CORPS CENTRAL
st.markdown("<h1 style='text-align: center; font-size: 36px; margin-top: 40px;'>Bonjour ! Je suis votre assistant IA.</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 18px;'>Comment puis-je vous aider aujourd'hui avec vos données ?</p>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="suggestion-box"><strong>📊 Volume global</strong>Déterminer le nombre exact de clients enregistrés dans la base.</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="suggestion-box"><strong>🏆 Performance produit</strong>Trouver la référence produit ou la marque la plus vendue.</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
question_utilisateur = st.text_input("", placeholder="Posez-moi votre question sur la base de données de ventes...")

prompt_systeme = """
Tu es un moteur Text-to-SQL pour PostgreSQL. Réponds UNIQUEMENT avec la requête SQL brute. Pas de phrases, pas de Markdown, pas de commentaires.
TABLES :
- clients : id_client, age_client, ville_client, pays_client, code_iso_client, sexe_client, nom_client
- produits : id_produit, nom_produit, categorie, sous_categorie, marque
- magasins : id_magasin, nom_magasin, ville_magasin, pays_magasin, continent_magasin, code_iso_magasin
- commandes : id_commande, date_commande, id_client, id_magasin, methode_paiement, mode_livraison
- ventes : id_commande, id_produit, quantite, prix_unitaire, remise, montant_ventes, profit, stock_disponible
JOINTURES :
- ventes.id_commande = commandes.id_commande
- ventes.id_produit = produits.id_produit
- commandes.id_client = clients.id_client
- commandes.id_magasin = magasins.id_magasin
"""



if question_utilisateur:
    historique_discussion = [
        {'role': 'system', 'content': prompt_systeme},
        {'role': 'user', 'content': "Combien de clients avons-nous ?"},
        {'role': 'assistant', 'content': "SELECT COUNT(*) FROM clients;"},
        {'role': 'user', 'content': question_utilisateur}
    ]

    with st.spinner("🤖 Traitement en cours..."):
        try:

            # ==========================
            # Temps Ollama
            # ==========================
            debut_llm = time.time()

            reponse = ollama.chat(
                model='mistral',
                messages=historique_discussion,
                options={
    "temperature": 0.0,
    "num_predict": 256
}
            )

            fin_llm = time.time()

            st.info(
                f"⏱️ Temps génération SQL (Ollama) : "
                f"{round(fin_llm - debut_llm, 2)} secondes"
            )

            requete_sql = reponse['message']['content'].strip()

            st.code(requete_sql, language="sql")

            if "SELECT" in requete_sql.upper():

                if "LIMIT" not in requete_sql.upper():
                    requete_sql = (
                        requete_sql.rstrip('; ')
                        + " LIMIT 100"
                    )

                # ==========================
                # Temps PostgreSQL
                # ==========================
                debut_sql = time.time()
                

                st.write("Type SQL :", type(requete_sql))
                st.write("SQL brut :")
                st.code(repr(requete_sql))

                df_resultat = pd.read_sql(
                    requete_sql,
                    engine
                ) 

                fin_sql = time.time()

                st.info(
                    f"⏱️ Temps PostgreSQL : "
                    f"{round(fin_sql - debut_sql, 2)} secondes"
                )

                st.markdown("### 📥 Résultat Analytique")

                if df_resultat.shape == (1, 1):
                    st.metric(
                        label="Indicateur Clé",
                        value=df_resultat.iloc[0, 0]
                    )
                else:
                    st.dataframe(
                        df_resultat,
                        use_container_width=True
                    )

            else:
                st.warning(
                    "⚠️ Le modèle n'a pas généré une requête SQL valide."
                )

        except Exception as e:
            st.error(f"Erreur : {e}")