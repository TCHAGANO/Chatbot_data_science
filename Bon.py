# app.py

import streamlit as st
import pandas as pd
import os
import base64
import time
import json
from datetime import datetime

# Importation de nos modules métiers (Séparation des responsabilités)
from database import initialiser_connexion
from llm import generer_requete_sql

# --- CONFIGURATION INTERFACE & LOOK LIGHT MODE PREMIUM ---
st.set_page_config(page_title="Assistant IA - Business Intelligence", page_icon="🤖", layout="wide")

# Dossier pour persister l'historique des discussions
HISTORY_DIR = "history"
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

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
        
        /* Photo de profil ultra-valorisée dans la sidebar */
        .sidebar-profile-container {
            text-align: center;
            padding: 15px 0;
            border-bottom: 1px solid #F1F5F9;
            margin-bottom: 15px;
        }
        .sidebar-profile-pic {
            border-radius: 50%;
            border: 3px solid #3B82F6;
            width: 110px; 
            height: 110px;
            object-fit: cover;
            box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.2);
            display: block;
            margin: 0 auto 10px auto;
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
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = f"chat_{int(time.time())}"

# --- FONCTIONS UTILES : SAUVEGARDE & CHARGEMENT ---
def sauvegarder_discussion_actuelle(titre_personnalise=None):
    if not st.session_state.messages:
        return
    
    if not titre_personnalise:
        premiere_question = st.session_state.messages[0]["content"]
        titre_personnalise = premiere_question[:30] + "..." if len(premiere_question) > 30 else premiere_question

    filepath = os.path.join(HISTORY_DIR, f"{st.session_state.current_chat_id}.json")
    
    messages_serialisables = []
    for m in st.session_state.messages:
        msg_copy = m.copy()
        if msg_copy.get("df_resultat") is not None and isinstance(msg_copy["df_resultat"], pd.DataFrame):
            msg_copy["df_resultat"] = msg_copy["df_resultat"].to_dict(orient="records")
        messages_serialisables.append(msg_copy)
        
    data = {
        "titre": titre_personnalise,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "messages": messages_serialisables
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def charger_discussion(chat_id):
    filepath = os.path.join(HISTORY_DIR, f"{chat_id}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        messages_reconstruits = []
        for m in data["messages"]:
            if m.get("df_resultat") is not None and isinstance(m["df_resultat"], list):
                m["df_resultat"] = pd.DataFrame(m["df_resultat"])
            messages_reconstruits.append(m)
            
        st.session_state.messages = messages_reconstruits
        st.session_state.current_chat_id = chat_id
        st.session_state.application_active = True

# --- FENÊTRE DE CONFIRMATION AVANT DE QUITTER (MODAL DIALOG) ---
@st.dialog("🚪 Confirmer la fermeture")
def modal_quitter():
    st.write("Voulez-vous vraiment clore cette session de chat ? Elle sera automatiquement archivée dans votre historique de gauche.")
    nom_archive = st.text_input("Donner un nom spécifique à cette discussion (optionnel) :", 
                                placeholder="Ex: Analyse Ventes France")
    
    col_back, col_confirm = st.columns(2)
    with col_back:
        if st.button("Annuler", use_container_width=True):
            st.rerun()
    with col_confirm:
        if st.button("Oui, sauvegarder et quitter", type="primary", use_container_width=True):
            sauvegarder_discussion_actuelle(titre_personnalise=nom_archive if nom_archive else None)
            st.session_state.messages = []
            st.session_state.current_chat_id = f"chat_{int(time.time())}"
            st.session_state.application_active = False
            st.rerun()

# --- BARRE LATÉRALE GAUCHE ---
with st.sidebar:
    st.markdown('<div class="sidebar-profile-container">', unsafe_allow_html=True)
    if os.path.exists("ma_photo.jpeg"):
        with open("ma_photo.jpeg", "rb") as img_file:
            encoded_img = base64.b64encode(img_file.read()).decode()
        st.markdown(f'<img src="data:image/jpeg;base64,{encoded_img}" class="sidebar-profile-pic">', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size: 50px; margin-bottom:10px;">👤</div>', unsafe_allow_html=True)
    
    st.markdown("<h3 style='color: #0F172A; font-size: 18px; font-weight:700; margin-bottom:0; text-align:center;'>📁 Aplot AI BI</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 13px; margin-top:0; text-align:center;'>Bahissou TCHAGNAO</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("🆕 New Chat", use_container_width=True):
            if st.session_state.messages:
                sauvegarder_discussion_actuelle()
            st.session_state.messages = []
            st.session_state.current_chat_id = f"chat_{int(time.time())}"
            st.session_state.application_active = True
            st.rerun()
    with col_nav2:
        if st.button("🚪 Close Chat", use_container_width=True, disabled=not st.session_state.messages):
            modal_quitter()

    st.markdown("---")
    
    st.markdown("<p style='color: #475569; font-size: 12px; font-weight: 600; margin-bottom:5px;'>🔍 RECHERCHER DANS L'HISTORIQUE</p>", unsafe_allow_html=True)
    search_query = st.text_input("Rechercher un mot clé...", label_visibility="collapsed", placeholder="Ex: chiffre d'affaires, clients...")

    history_files = [f for f in os.listdir(HISTORY_DIR) if f.endswith(".json")]
    all_chats = []
    
    for f in history_files:
        cid = f.replace(".json", "")
        with open(os.path.join(HISTORY_DIR, f), "r", encoding="utf-8") as file_data:
            try:
                js = json.load(file_data)
                all_chats.append({"id": cid, "titre": js["titre"], "date": js["date"]})
            except:
                pass
                
    all_chats = sorted(all_chats, key=lambda x: x["date"], reverse=True)
    
    if search_query:
        all_chats = [c for c in all_chats if search_query.lower() in c["titre"].lower()]

    st.markdown("<p style='color: #475569; font-size: 12px; font-weight: 600; margin-top:15px; margin-bottom:5px;'>🕒 DISCUSSIONS RÉCENTES</p>", unsafe_allow_html=True)
    
    if all_chats:
        for chat in all_chats:
            nom_bouton = f"💬 {chat['titre']}"
            if len(nom_bouton) > 28:
                nom_bouton = nom_bouton[:25] + "..."
                
            type_bouton = "primary" if st.session_state.current_chat_id == chat["id"] else "secondary"
            
            if st.button(nom_bouton, key=f"hist_{chat['id']}", use_container_width=True, type=type_bouton):
                charger_discussion(chat["id"])
                st.rerun()
    else:
        st.markdown("<p style='color: #94A3B8; font-size: 12px; font-style: italic;'>Aucun chat trouvé.</p>", unsafe_allow_html=True)

    st.markdown("<br>" * 2, unsafe_allow_html=True)
    st.markdown("---")
    st.link_button("💼 Profil LinkedIn", "https://www.linkedin.com/in/bahissou-tchagnao-9a91492aa", use_container_width=True)
    st.link_button("💻 Repository GitHub", "https://github.com/TCHAGANO/Chatbot_data_science.git", use_container_width=True)

# --- RECONSTRUCTION DE L'HISTORIQUE ---
for idx, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        statut_avatar = "🔵" if msg.get("status_ok", True) else "🔴"
        
        with st.chat_message("assistant", avatar=statut_avatar):
            if msg.get("is_sql", True) and msg.get("df_resultat") is not None:
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Résultat & Analytics", "🗄 Code SQL", "🤖 Métriques IA", "📈 Visualisation Graphique"])
                
                with tab1:
                    df = msg["df_resultat"]
                    if df.empty:
                        st.warning("La base de données a retourné un tableau vide pour cette requête.")
                    elif df.shape == (1, 1):
                        valeur_brute = df.iloc[0, 0]
                        nom_colonne = df.columns[0].replace('_', ' ').title()
                        
                        if any(x in df.columns[0].lower() for x in ['montant', 'profit', 'prix', 'ventes']):
                            st.metric(label=f"💰 {nom_colonne}", value=f"{valeur_brute:,.2f} €")
                        else:
                            st.metric(label=f"🔢 {nom_colonne}", value=f"{valeur_brute:,}")
                    else:
                        st.dataframe(df, use_container_width=True)
                        
                        csv_data = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Extraire les données au format CSV",
                            data=csv_data,
                            file_name="extraction_bi_chatbot.csv",
                            mime="text/csv",
                            key=f"dl_{time.time()}_{idx}"
                        )
                        
                with tab2:
                    st.code(msg["query_sql"], language="sql")
                with tab3:
                    st.info(msg["analytics_text"])
                    
                with tab4:
                    df = msg["df_resultat"]
                    if df is not None and not df.empty and df.shape != (1, 1):
                        st.markdown("### 📊 Générateur Visuel à la Demande")
                        
                        if st.button("👁️ Générer l'analyse visuelle", key=f"btn_chart_{time.time()}_{idx}"):
                            colonnes_num = df.select_dtypes(include=['number']).columns
                            
                            if not colonnes_num.empty:
                                col_val = colonnes_num[0]
                                col_date = [c for c in df.columns if 'date' in c.lower() or 'annee' in c.lower() or 'mois' in c.lower()]
                                
                                if col_date:
                                    st.markdown(f"##### 📈 Évolution temporelle ({col_val})")
                                    st.line_chart(df.set_index(col_date[0])[col_val])
                                elif len(df.columns) > 1:
                                    col_axe_x = [c for c in df.columns if c != col_val][0]
                                    st.markdown(f"##### 📊 Analyse comparative par {col_axe_x.replace('_', ' ')}")
                                    st.bar_chart(df.set_index(col_axe_x)[col_val])
                            else:
                                st.warning("Les données extraites ne contiennent pas d'indicateurs numériques exploitables.")
                    else:
                        st.info("Cette réponse ne contient pas le format requis pour générer un graphique.")
            else:
                st.markdown(msg["content"])

# --- ACCUEIL BIENVENUE & BENTO GRID ---
if len(st.session_state.messages) == 0:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #3B82F6; font-weight: 600; margin-bottom: 0; font-size:14px;'>Welcome to BI Chatbot Pro</p>", unsafe_allow_html=True)
    st.markdown("<h1 class='hero-title' style='margin-top: 0;'>How Can I Assist You Today?</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    card_col1, card_col2, card_col3, card_col4 = st.columns(4)
    with card_col1: st.markdown('<div class="bento-card card-green"><div class="bento-title title-green">📊 Volume Global</div><div class="bento-desc">Déterminez le nombre exact de clients ou de commandes.</div></div>', unsafe_allow_html=True)
    with card_col2: st.markdown('<div class="bento-card card-blue"><div class="bento-title title-blue">🏆 Top Performances</div><div class="bento-desc">Trouvez la référence produit ou la marque la plus vendue.</div></div>', unsafe_allow_html=True)
    with card_col3: st.markdown('<div class="bento-card card-purple"><div class="bento-title title-purple">🎯 Profils Clients</div><div class="bento-desc">Analysez la répartition des acheteurs par ville ou sexe.</div></div>', unsafe_allow_html=True)
    with card_col4: st.markdown('<div class="bento-card card-orange"><div class="bento-title title-orange">💸 Analyse CA & Marge</div><div class="bento-desc">Calculez les profits et observez l\'impact des remises.</div></div>', unsafe_allow_html=True)

# --- ZONE DE CAPTURE DE LA SAISIE ---
if st.session_state.application_active:
    st.markdown("""
        <div style='display: flex; gap: 8px; margin-bottom: -10px; justify-content: center;'>
            <span style='background: #E2E8F0; color: #475569; font-size: 11px; padding: 4px 12px; border-radius: 20px; font-weight: 500;'>⚡ Fast Mode</span>
            <span style='background: #E2E8F0; color: #475569; font-size: 11px; padding: 4px 12px; border-radius: 20px; font-weight: 500;'>🔍 Deep SQL Check</span>
            <span style='background: #E2E8F0; color: #475569; font-size: 11px; padding: 4px 12px; border-radius: 20px; font-weight: 500;'>🕒 Session Tracker</span>
        </div>
    """, unsafe_allow_html=True)

    question_utilisateur = st.chat_input("Posez votre question...")

    if question_utilisateur:
        st.session_state.messages.append({"role": "user", "content": question_utilisateur})
        st.rerun()



# --- PIPELINE DE TRAITEMENT BACKEND ---
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and st.session_state.application_active:
    with st.chat_message("assistant"):
        with st.spinner("🤖 Réflexion de l'assistant en cours..."):
            try:
                debut_llm = time.time()
                # Appelle llm.py qui renvoie un dictionnaire {"sql": ..., "commentaire": ...}
                reponse_structuree = generer_requete_sql(st.session_state.messages)
                fin_llm = time.time()

                requete_sql = reponse_structuree.get("sql")
                phrase_commentaire = reponse_structuree.get("commentaire", "Voici les résultats :")

                # Si une requête SQL valide est extraite
                if requete_sql and "SELECT" in requete_sql.upper():
                    if "LIMIT" not in requete_sql.upper():
                        requete_sql = requete_sql.rstrip('; ') + " LIMIT 100;"

                    debut_sql = time.time()
                    df_resultat = pd.read_sql(requete_sql, engine)
                    fin_sql = time.time()

                    txt_performance = f"Génération SQL : {round(fin_llm - debut_llm, 2)}s | Base de données : {round(fin_sql - debut_sql, 2)}s."
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": phrase_commentaire,  # <--- CORRECTION : Affiche la phrase précise de l'IA
                        "is_sql": True,
                        "df_resultat": df_resultat,
                        "query_sql": requete_sql,
                        "analytics_text": txt_performance,
                        "status_ok": True
                    })
                else:
                    # Cas d'une réponse conversationnelle simple (sans SQL)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": phrase_commentaire,
                        "is_sql": False,
                        "df_resultat": None,
                        "query_sql": None,
                        "analytics_text": "Analyse conversationnelle directe.",
                        "status_ok": True
                    })
                sauvegarder_discussion_actuelle()
                st.rerun()
                
            except Exception as e:
                message_propre = "⚠️ Une erreur est survenue lors de l'exécution de la requête SQL."
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": message_propre,
                    "is_sql": False,
                    "df_resultat": None,
                    "query_sql": None,
                    "analytics_text": f"Erreur système interceptée : {e}",
                    "status_ok": False
                })
                sauvegarder_discussion_actuelle()
                st.rerun()

                ###################################################

                # llm.py
import ollama
import json
from prompts import PROMPT_SYSTEME

def generer_requete_sql(messages_historique):
    """
    Génère une réponse structurée JSON contenant du SQL valide et un commentaire.
    Filtre et sécurise l'historique avant l'envoi à Ollama.
    """
    # 1. Initialisation avec le prompt système contenant votre schéma officiel
    messages_pour_ollama = [{"role": "system", "content": PROMPT_SYSTEME}]
    
    # 2. Nettoyage strict de l'historique pour Ollama (uniquement du texte brut)
    for msg in messages_historique:
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            # On s'assure de ne passer que des chaînes de caractères pures
            contenu_texte = str(msg["content"])
            messages_pour_ollama.append({
                "role": msg["role"],
                "content": contenu_texte
            })
        
    try:
        # 3. Appel du modèle Mistral au format JSON strict
        response = ollama.chat(
            model="mistral",
            messages=messages_pour_ollama,
            options={
                "temperature": 0.0  # Température à 0 pour bloquer toute hallucination de colonnes
            },
            format="json"
        )
        
        # 4. Décodage et renvoi de la structure à app.py
        contenu_brut = response['message']['content'].strip()
        return json.loads(contenu_brut)

    except Exception as e:
        # En cas d'anomalie, on renvoie une structure JSON compatible avec app.py
        return {
            "sql": None,
            "commentaire": f"Désolé Bahissou, j'ai rencontré une difficulté lors de l'analyse de votre demande. (Détails : {str(e)})"
        }
    
    ###############################################################################

    PROMPT_SYSTEME = """
Tu es un assistant expert en Business Intelligence pour l'application Aplot AI BI.
Tu dois impérativement répondre au format JSON strict avec exactement ces deux clés :
{
    "sql": "La requête PostgreSQL pure sur une seule ligne (ou null si aucune donnée n'est requise)",
    "commentaire": "Une phrase précise en français qui introduit les données à l'utilisateur"
}

Voici le schéma EXACT de la base de données PostgreSQL :
1. Table 'clients' : id_client, age_client, ville_client, pays_client, code_iso_client, sexe_client, nom_client
2. Table 'produits' : id_produit, nom_produit, categorie, sous_categorie, marque
3. Table 'magasins' : id_magasin, nom_magasin, ville_magasin, pays_magasin, continent_magasin, code_iso_magasin
4. Table 'commandes' : id_commande, date_commande, id_client, id_magasin, methode_paiement, mode_livraison
5. Table 'ventes' : id_commande, id_produit, quantite, prix_unitaire, remise, montant_ventes, profit, stock_disponible

JOINTURES ABSOLUES :
- ventes.id_commande = commandes.id_commande
- ventes.id_produit = produits.id_produit
- commandes.id_client = clients.id_client
- commandes.id_magasin = magasins.id_magasin

Règles de génération strictes :
- N'ajoute AUCUN texte, bloc markdown (```sql) ou commentaire en dehors du JSON.
- Pour chercher une première lettre, utilise l'opérateur ILIKE avec '%'. Exemple : WHERE marque ILIKE 'A%'
- Pour extraire une année : EXTRACT(YEAR FROM date_commande) = 2022
- Pour les volumes de ventes, fais un SUM(quantite). Pour le chiffre d'affaires, fais un SUM(montant_ventes).

Exemple de JSON attendu :
{
    "sql": "SELECT DISTINCT pays_client FROM clients;",
    "commentaire": "Voici la liste des pays d'origine de nos clients :"
}
"""