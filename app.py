import streamlit as st
import ollama
import pandas as pd
from sqlalchemy import create_engine
import urllib.parse
import os
import base64  # <--- Ajouté proprement ici !

# 1. Configuration de la page Web (Thème large et sombre natif)
st.set_page_config(page_title="Assistant IA - Business Intelligence", page_icon="🤖", layout="wide")

# --- INJECTION CSS PURE POUR COLLER À L'IMAGE DE RÉFÉRENCE ---
st.markdown("""
    <style>
        /* Fond principal ultra sombre */
        .stApp {
            background-color: #0B0E14 !important;
            color: #E2E8F0 !important;
        }
        
        /* Barre latérale droite / gauche style Dashboard */
        section[data-testid="stSidebar"] {
            background-color: #06080C !important;
            border-right: 1px solid #1E293B !important;
        }
        
        /* Zone d'entrée de texte de la question */
        div[data-baseweb="input"] {
            background-color: #111827 !important;
            border: 2px solid #1F2937 !important;
            border-radius: 24px !important; /* Arrondi style pilule */
            color: #FFFFFF !important;
            padding: 4px 12px;
        }
        div[data-baseweb="input"]:focus-within {
            border-color: #3B82F6 !important; /* Reflet bleu de l'image */
            box-shadow: 0 0 10px rgba(59, 130, 246, 0.5) !important;
        }
        
        /* Cartes de suggestions (Boutons fictifs du centre) */
        .suggestion-box {
            background-color: #111827;
            border: 1px solid #1F2937;
            border-radius: 12px;
            padding: 15px;
            text-align: left;
            min-height: 80px;
            color: #9CA3AF;
            font-size: 14px;
            cursor: pointer;
        }
        .suggestion-box strong {
            color: #E5E7EB;
            display: block;
            margin-bottom: 4px;
        }
        
        /* Masquer les bordures Streamlit inutiles */
        #MainMenu, footer, header {visibility: hidden;}
        
        /* Photo de profil circulaire */
        .profile-pic {
            border-radius: 50%;
            border: 3px solid #3B82F6;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 120px;
            height: 120px;
            object-fit: cover;
        }
        
        /* Bloc KPI unique */
        .kpi-container {
            background-color: #111827;
            border: 1px solid #3B82F6;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# 2. Connexion PostgreSQL en arrière-plan
@st.cache_resource
def initialiser_connexion():
    password = urllib.parse.quote_plus("Bahiss@u02gnao")
    return create_engine(f"postgresql://postgres:{password}@localhost:5432/chatbot_db")

engine = initialiser_connexion()

# --- BARRE LATÉRALE GAUCHE (PROFIL ET HISTORIQUE D'EXPLORATION) ---

# --- BARRE LATÉRALE GAUCHE (PROFIL ET HISTORIQUE D'EXPLORATION) ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gestion propre de la photo de profil circulaire
    if os.path.exists("ma_photo.jpg"):
        with open("ma_photo.jpg", "rb") as img_file:
            encoded_img = base64.b64encode(img_file.read()).decode()
        st.markdown(f'<img src="data:image/jpeg;base64,{encoded_img}" class="profile-pic">', unsafe_allow_html=True)
    elif os.path.exists("ma_photo.png"):
        with open("ma_photo.png", "rb") as img_file:
            encoded_img = base64.b64encode(img_file.read()).decode()
        st.markdown(f'<img src="data:image/png;base64,{encoded_img}" class="profile-pic">', unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align:center; color:#6B7280; padding:20px; border:1px dashed #1E293B; border-radius:50%; width:120px; height:120px; margin:auto;'>[Photo]</div>", unsafe_allow_html=True)
        
    st.markdown("<h3 style='text-align: center; color: white; margin-bottom:0;'>Bahissou TCHAGNAO</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #3B82F6; font-size:14px; margin-top:0;'>Êtudiant en Data Science</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #1E293B;'/>", unsafe_allow_html=True)

# 3. CORPS CENTRAL DE L'INTERFACE (Style Dashboard Moderne)
st.markdown("<h1 style='text-align: center; font-size: 36px; margin-top: 40px;'>Bonjour ! Je suis votre assistant IA.</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 18px;'>Comment puis-je vous aider aujourd'hui avec vos données ?</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Grille de Suggestions de requêtes (Comme sur l'image de référence, mais en Français)
col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="suggestion-box"><strong>📊 Volume global</strong>Déterminer le nombre exact de clients enregistrés dans la base.</div>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<div class="suggestion-box"><strong>🌍 Analyse géographique</strong>Identifier les performances de ventes par pays ou par ville.</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="suggestion-box"><strong>🏆 Performance produit</strong>Trouver la référence produit ou la marque la plus vendue.</div>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<div class="suggestion-box"><strong>💰 Analyse financière</strong>Calculer le chiffre d\'affaires ou le profit d\'une période.</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Barre d'analyse (Input utilisateur)
question_utilisateur = st.text_input("", placeholder="Posez-moi votre question sur la base de données de ventes...")

# Schéma strict pour le moteur SQL
prompt_systeme = """
Tu es un moteur Text-to-SQL pour PostgreSQL. Réponds UNIQUEMENT avec la requête SQL brute. Pas de phrases, pas de Markdown, pas de commentaires.
Si la question n'a aucun rapport avec la base de données, réponds : "ERREUR"

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
    # Banque de 10 exemples stratégiques pour l'IA
    historique_discussion = [
        {'role': 'system', 'content': prompt_systeme},
        {'role': 'user', 'content': "Combien de clients avons-nous ?"},
        {'role': 'assistant', 'content': "SELECT COUNT(*) FROM clients;"},
        {'role': 'user', 'content': "Quels sont les 5 clients les plus âgés ?"},
        {'role': 'assistant', 'content': "SELECT nom_client, age_client FROM clients ORDER BY age_client DESC LIMIT 5;"},
        {'role': 'user', 'content': "Quel est le produit le plus vendu ?"},
        {'role': 'assistant', 'content': "SELECT p.nom_produit, SUM(v.quantite) AS total_vendu FROM ventes v JOIN produits p ON v.id_produit = p.id_produit GROUP BY p.nom_produit ORDER BY total_vendu DESC LIMIT 1;"},
        {'role': 'user', 'content': "Quel est le chiffre d'affaires total pour la marque Apple ?"},
        {'role': 'assistant', 'content': "SELECT SUM(v.montant_ventes) FROM ventes v JOIN produits p ON v.id_produit = p.id_produit WHERE p.marque = 'Apple';"},
        {'role': 'user', 'content': "Donne moi le nom du plus riche des clients"},
        {'role': 'assistant', 'content': "SELECT c.nom_client, SUM(v.montant_ventes) AS total_depense FROM ventes v JOIN commandes co ON v.id_commande = co.id_commande JOIN clients c ON co.id_client = c.id_client GROUP BY c.nom_client ORDER BY total_depense DESC LIMIT 1;"},
        {'role': 'user', 'content': "Quel est le montant des ventes par ville de magasin ?"},
        {'role': 'assistant', 'content': "SELECT m.ville_magasin, SUM(v.montant_ventes) AS total_ventes FROM ventes v JOIN commandes c ON v.id_commande = c.id_commande JOIN magasins m ON c.id_magasin = m.id_magasin GROUP BY m.ville_magasin ORDER BY total_ventes DESC;"},
        {'role': 'user', 'content': "Combien de ventes ont été réalisées en 2025 ?"},
        {'role': 'assistant', 'content': "SELECT COUNT(*) FROM ventes v JOIN commandes c ON v.id_commande = c.id_commande WHERE c.date_commande BETWEEN '2025-01-01' AND '2025-12-31';"},
        {'role': 'user', 'content': "Quelle catégorie de produit génère le plus de profit ?"},
        {'role': 'assistant', 'content': "SELECT p.categorie, SUM(v.profit) AS profit_total FROM ventes v JOIN produits p ON v.id_produit = p.id_produit GROUP BY p.categorie ORDER BY profit_total DESC LIMIT 1;"},
        {'role': 'user', 'content': "Trouve les produits qui sont des tablettes"},
        {'role': 'assistant', 'content': "SELECT nom_produit FROM produits WHERE nom_produit ILIKE '%tablette%';"},
        {'role': 'user', 'content': "Quelle est la répartition des ventes par sexe ?"},
        {'role': 'assistant', 'content': "SELECT cl.sexe_client, SUM(v.montant_ventes) FROM ventes v JOIN commandes co ON v.id_commande = co.id_commande JOIN clients cl ON co.id_client = cl.id_client GROUP BY cl.sexe_client;"},
        {'role': 'user', 'content': question_utilisateur}
    ]
    
    with st.spinner("🤖 Traitement de la requête business..."):
        try:
            reponse = ollama.chat(model='mistral', messages=historique_discussion)
            requete_sql = reponse['message']['content'].strip()
            
            # Condition de sécurité : Si l'IA ne génère pas de SELECT ou dit ERREUR, message court exigé :
            if "ERREUR" in requete_sql or not requete_sql.upper().startswith("SELECT"):
                st.warning("⚠️ Veuillez reformuler votre question.")
            else:
                # Exécution sur PostgreSQL
                df_resultat = pd.read_sql(requete_sql, engine)
                
                st.markdown("### 📥 Résultat Analytique")
                
                # Cas 1 : Résultat unique (Ex: Nombre de clients)
                if df_resultat.shape == (1, 1):
                    valeur = df_resultat.iloc[0, 0]
                    st.markdown(f"""
                        <div class="kpi-container">
                            <p style="color:#9CA3AF; font-size:14px; margin:0; text-transform:uppercase;">Indicateur Clé</p>
                            <h1 style="color:#3B82F6 !important; font-size:48px; margin:10px 0 0 0;">{valeur:,}</h1>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Cas 2 : Tableaux et Graphiques
                else:
                    col_gauche, col_droite = st.columns(2)
                    with col_gauche:
                        st.dataframe(df_resultat, use_container_width=True)
                    with col_droite:
                        if len(df_resultat) > 1 and len(df_resultat.columns) >= 2:
                            cx, cy = df_resultat.columns[0], df_resultat.columns[1]
                            if pd.api.types.is_numeric_dtype(df_resultat[cy]):
                                st.bar_chart(data=df_resultat, x=cx, y=cy, use_container_width=True)
                                
                # Rappel technique masqué
                with st.expander("🛠️ Inspecter le code SQL exécuté"):
                    st.code(requete_sql, language="sql")
                    
        except Exception:
            # En cas de crash inattendu, on applique votre consigne stricte de message court
            st.warning("⚠️ Veuillez reformuler votre question.")