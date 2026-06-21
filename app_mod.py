# app.py
# Fichier situé à la racine : C:\Users\Bahissou TCHAGNAO\Desktop\Chatbot_project\Chatbot_data_science\app.py

from decimal import Decimal
from sqlalchemy import text
import hashlib
import re
import streamlit as st
import pandas as pd
import os
import base64
import time
import json
from datetime import datetime

from database_connexion import initialiser_connexion
from llm import generer_requete_sql
from sql_security import valider_requete_sql

# ==================== CONFIGURATION ====================
st.set_page_config(page_title="Assistant IA - Business Intelligence", page_icon="🤖", layout="wide")

# Dossier d'historique
HISTORY_DIR = "history"
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

# ==================== STYLES CSS ====================
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC !important; color: #1E293B !important; }
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    .bento-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 20px;
        min-height: 140px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
        transition: all 0.2s ease-in-out;
        position: relative;
        overflow: hidden;
        cursor: pointer;
    }
    .bento-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        border-color: #CBD5E1;
    }
    .bento-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; height: 4px;
    }
    .card-green::before { background: linear-gradient(90deg, #4ADE80, #22C55E); }
    .card-blue::before { background: linear-gradient(90deg, #60A5FA, #3B82F6); }
    .card-purple::before { background: linear-gradient(90deg, #C084FC, #A855F7); }
    .card-orange::before { background: linear-gradient(90deg, #FB923C, #F97316); }

    .bento-title { font-size: 15px; font-weight: 600; margin-bottom: 6px; }
    .title-green { color: #166534; }
    .title-blue { color: #1E40AF; }
    .title-purple { color: #6B21A8; }
    .title-orange { color: #9A3412; }

    .bento-desc { color: #64748B; font-size: 13px; line-height: 1.4; }
    .hero-title { font-size: 32px; font-weight: 700; color: #0F172A; text-align: center; margin-top: 20px; }

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
        box-shadow: 0 10px 15px -3px rgba(59,130,246,0.2);
        display: block;
        margin: 0 auto 10px auto;
    }
    div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05) !important;
    }
    div[data-baseweb="input"]:focus-within { border-color: #3B82F6 !important; }
    #MainMenu, footer, header { visibility: hidden; }

    .nav-button {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 8px 16px !important;
        color: #1E293B !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }
    .nav-button:hover {
        background-color: #F1F5F9 !important;
        border-color: #94A3B8 !important;
    }
    .nav-button:disabled { opacity: 0.4 !important; cursor: not-allowed !important; }
</style>
""", unsafe_allow_html=True)

# ==================== CONNEXION À LA BASE ====================
engine = initialiser_connexion()

# ==================== ÉTAT DE LA SESSION ====================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "application_active" not in st.session_state:
    st.session_state.application_active = True
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = f"chat_{int(time.time())}"
if "sql_cache" not in st.session_state:
    st.session_state.sql_cache = {}

# Navigation
if "show_all_messages" not in st.session_state:
    st.session_state.show_all_messages = True
if "message_index" not in st.session_state:
    st.session_state.message_index = -1

# ==================== FONCTIONS UTILITAIRES ====================

def serialiseur_json_personnalise(obj):
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")
    if isinstance(obj, Decimal):
        return float(obj)
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    if isinstance(obj, (set, frozenset)):
        return list(obj)
    raise TypeError(f"Type {obj.__class__.__name__} non sérialisable")

def deduplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = list(df.columns)
    seen = {}
    new_cols = []
    for col in cols:
        if col not in seen:
            seen[col] = 1
            new_cols.append(col)
        else:
            seen[col] += 1
            new_cols.append(f"{col}_{seen[col]}")
    df.columns = new_cols
    return df

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
            df_temp = msg_copy["df_resultat"].copy()
            for col in df_temp.select_dtypes(include=['datetime', 'datetimetz']).columns:
                df_temp[col] = df_temp[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            for col in df_temp.select_dtypes(include=['object', 'string']).columns:
                if df_temp[col].apply(lambda x: isinstance(x, Decimal)).any():
                    df_temp[col] = df_temp[col].apply(lambda x: float(x) if isinstance(x, Decimal) else x)
            msg_copy["df_resultat"] = df_temp.to_dict(orient="records")
        messages_serialisables.append(msg_copy)

    data = {
        "titre": titre_personnalise,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "messages": messages_serialisables
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4, default=serialiseur_json_personnalise)

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
        st.session_state.show_all_messages = True
        st.session_state.message_index = -1

@st.dialog("🚪 Confirmer la fermeture")
def modal_quitter():
    st.write("Voulez-vous vraiment clore cette session ? Elle sera archivée dans l'historique.")
    nom_archive = st.text_input("Nom (optionnel) :", placeholder="Ex: Analyse Ventes France")
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

@st.dialog("⚠️ Confirmer la suppression définitive")
def dialog_supprimer_tout():
    st.warning("Cette action est irréversible. Toutes les conversations seront supprimées.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ Annuler", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("🗑️ Oui, tout supprimer", type="primary", use_container_width=True):
            for f in os.listdir(HISTORY_DIR):
                if f.endswith(".json"):
                    os.remove(os.path.join(HISTORY_DIR, f))
            st.cache_data.clear()
            st.session_state.messages = []
            st.session_state.current_chat_id = f"chat_{int(time.time())}"
            st.rerun()

# ==================== CACHE DE L'HISTORIQUE ====================
@st.cache_data(ttl=60)
def get_all_chats_cached():
    if not os.path.exists(HISTORY_DIR):
        return []
    history_files = [f for f in os.listdir(HISTORY_DIR) if f.endswith(".json")]
    chats = []
    for f in history_files:
        cid = f.replace(".json", "")
        try:
            with open(os.path.join(HISTORY_DIR, f), "r", encoding="utf-8") as file_data:
                js = json.load(file_data)
                chats.append({"id": cid, "titre": js["titre"], "date": js["date"]})
        except Exception:
            pass
    return sorted(chats, key=lambda x: x["date"], reverse=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    # Profil
    st.markdown('<div class="sidebar-profile-container">', unsafe_allow_html=True)
    if os.path.exists("ma_photo.jpg"):
        with open("ma_photo.jpg", "rb") as img_file:
            encoded_img = base64.b64encode(img_file.read()).decode()
        st.markdown(f'<img src="data:image/jpeg;base64,{encoded_img}" class="sidebar-profile-pic">', unsafe_allow_html=True)
    elif os.path.exists("ma_photo.jpeg"):
        with open("ma_photo.jpeg", "rb") as img_file:
            encoded_img = base64.b64encode(img_file.read()).decode()
        st.markdown(f'<img src="data:image/jpeg;base64,{encoded_img}" class="sidebar-profile-pic">', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:50px; margin-bottom:10px;">👤</div>', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#0F172A; font-size:18px; font-weight:700; text-align:center;'>📁 Aplot AI BI</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748B; font-size:13px; text-align:center;'>Bahissou TCHAGNAO</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Navigation
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("🆕 New Chat", use_container_width=True):
            if st.session_state.messages:
                sauvegarder_discussion_actuelle()
            st.session_state.messages = []
            st.session_state.current_chat_id = f"chat_{int(time.time())}"
            st.session_state.application_active = True
            st.session_state.show_all_messages = True
            st.session_state.message_index = -1
            st.rerun()
    with col_nav2:
        if st.button("🚪 Close Chat", use_container_width=True, disabled=not st.session_state.messages):
            modal_quitter()

    st.markdown("---")

    # Recherche
    st.markdown("<p style='color:#475569; font-size:12px; font-weight:600;'>🔍 RECHERCHER DANS L'HISTORIQUE</p>", unsafe_allow_html=True)
    search_query = st.text_input("Rechercher un mot clé...", label_visibility="collapsed", placeholder="Ex: chiffre d'affaires, clients...")

    all_chats = get_all_chats_cached()
    if search_query:
        all_chats = [c for c in all_chats if search_query.lower() in c["titre"].lower()]

    st.markdown("<p style='color:#475569; font-size:12px; font-weight:600; margin-top:15px;'>🕒 DISCUSSIONS RÉCENTES</p>", unsafe_allow_html=True)
    MAX_HISTORY = 20
    afficher_chats = all_chats[:MAX_HISTORY]
    nb_total = len(all_chats)

    if afficher_chats:
        for chat in afficher_chats:
            nom_bouton = f"💬 {chat['titre']}"
            if len(nom_bouton) > 28:
                nom_bouton = nom_bouton[:25] + "..."
            type_bouton = "primary" if st.session_state.current_chat_id == chat["id"] else "secondary"
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(nom_bouton, key=f"hist_{chat['id']}", use_container_width=True, type=type_bouton):
                    charger_discussion(chat["id"])
                    st.rerun()
            with col2:
                if st.button("🗑", key=f"del_{chat['id']}", help="Supprimer cette discussion"):
                    os.remove(os.path.join(HISTORY_DIR, f"{chat['id']}.json"))
                    st.cache_data.clear()
                    st.rerun()
        if nb_total > MAX_HISTORY:
            st.caption(f"{nb_total} discussions au total. Seules les {MAX_HISTORY} plus récentes sont affichées.")
    else:
        st.markdown("<p style='color:#94A3B8; font-size:12px; font-style:italic;'>Aucun chat trouvé.</p>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🗑️ Tout supprimer", use_container_width=True, type="secondary"):
        dialog_supprimer_tout()

    st.markdown("---")
    st.link_button("💼 Profil LinkedIn", "https://www.linkedin.com/in/bahissou-tchagnao-9a91492aa", use_container_width=True)
    st.link_button("💻 Repository GitHub", "https://github.com/TCHAGANO/Chatbot_data_science.git", use_container_width=True)

    # ==================== ADMINISTRATION (AJOUT / SUPPRESSION) ====================
    st.markdown("---")
    with st.expander("🔐 Administration des clients", expanded=False):
        admin_password = st.text_input("Mot de passe admin", type="password", key="admin_pass")
        
        access_granted = False
        try:
            if admin_password == st.secrets["ADMIN_PASSWORD"]:
                st.success("✅ Accès autorisé")
                access_granted = True
            elif admin_password:
                st.warning("⛔ Accès refusé.")
        except KeyError:
            st.error("❌ Mot de passe admin non configuré. Ajoute ADMIN_PASSWORD dans secrets.toml.")

        if access_granted:
            # Ajout
            st.subheader("➕ Ajouter un client")
            with st.form("form_ajout_client"):
                nom = st.text_input("Nom complet")
                age = st.number_input("Âge", min_value=0, max_value=120, step=1)
                sexe = st.selectbox("Sexe", ["M", "F"])
                ville = st.text_input("Ville")
                pays = st.text_input("Pays")
                code_iso = st.text_input("Code ISO (ex: FR, NG)", max_chars=3)
                submitted = st.form_submit_button("Ajouter ce client")
                if submitted:
                    if not nom or not pays:
                        st.error("Le nom et le pays sont obligatoires.")
                    else:
                        try:
                            with engine.begin() as conn:
                                conn.execute(
                                    text("""
                                        INSERT INTO clients (nom_client, age_client, sexe_client, ville_client, pays_client, code_iso_client)
                                        VALUES (:nom, :age, :sexe, :ville, :pays, :code_iso)
                                    """),
                                    {"nom": nom, "age": age, "sexe": sexe, "ville": ville, "pays": pays, "code_iso": code_iso.upper()}
                                )
                            st.success(f"✅ Client '{nom}' ajouté !")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur : {e}")

            st.markdown("---")

            # Suppression
            st.subheader("🗑️ Supprimer un client")
            with engine.connect() as conn:
                clients_df = pd.read_sql("SELECT id_client, nom_client FROM clients ORDER BY nom_client", conn)
            if clients_df.empty:
                st.info("Aucun client dans la base.")
            else:
                client_dict = dict(zip(clients_df["nom_client"], clients_df["id_client"]))
                selected_name = st.selectbox("Choisir un client à supprimer", list(client_dict.keys()))
                if st.button("🗑️ Supprimer définitivement", type="primary", use_container_width=True):
                    client_id = client_dict[selected_name]
                    try:
                        with engine.begin() as conn:
                            check = conn.execute(text("SELECT COUNT(*) FROM commandes WHERE id_client = :id"), {"id": client_id}).scalar()
                            if check > 0:
                                st.error(f"❌ Impossible : {selected_name} a {check} commande(s) associée(s).")
                            else:
                                conn.execute(text("DELETE FROM clients WHERE id_client = :id"), {"id": client_id})
                                st.success(f"✅ Client '{selected_name}' supprimé !")
                                time.sleep(1)
                                st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erreur : {e}")

# ==================== FONCTION D'AFFICHAGE D'UN MESSAGE ====================
def afficher_message(msg):
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        statut_avatar = "🔵" if msg.get("status_ok", True) else "🔴"
        with st.chat_message("assistant", avatar=statut_avatar):
            if msg.get("is_sql", True) and msg.get("df_resultat") is not None:
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Résultat & Analytics", "🗄 Code SQL", "🤖 Métriques IA", "📈 Visualisation Graphique"])
                with tab1:
                    df = pd.DataFrame(msg["df_resultat"]) if isinstance(msg["df_resultat"], list) else msg["df_resultat"]
                    if df.empty:
                        st.warning("Aucune donnée disponible.")
                    elif df.shape == (1, 1):
                        valeur_brute = df.iloc[0, 0]
                        nom_colonne = df.columns[0].replace('_', ' ').title()
                        if valeur_brute is None or (isinstance(valeur_brute, float) and pd.isna(valeur_brute)):
                            st.metric(label=f"🔢 {nom_colonne}", value="Aucune donnée")
                        else:
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
                            key=f"dl_{hash(str(msg))}"
                        )
                with tab2:
                    st.code(msg.get("query_sql") or "Aucune requête SQL", language="sql")
                with tab3:
                    st.info(msg.get("analytics_text", "Aucune métrique disponible."))
                with tab4:
                    df = pd.DataFrame(msg["df_resultat"]) if isinstance(msg["df_resultat"], list) else msg["df_resultat"]
                    if df is not None and not df.empty and df.shape != (1, 1):
                        st.markdown("### 📊 Générateur Visuel à la Demande")
                        if st.button("👁️ Générer l'analyse visuelle", key=f"btn_chart_{hash(str(msg))}"):
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
                                st.warning("Pas d'indicateur numérique exploitable.")
                    else:
                        st.info("Pas assez de données pour générer un graphique.")
            else:
                st.markdown(msg["content"])
                if not msg.get("status_ok", True) and msg.get("analytics_text"):
                    st.error(msg["analytics_text"])

# ==================== AFFICHAGE DE LA DISCUSSION ====================
messages = st.session_state.messages
total = len(messages)

if total > 0:
    if st.session_state.show_all_messages:
        for msg in messages:
            afficher_message(msg)
    else:
        idx = st.session_state.message_index
        if 0 <= idx < total:
            afficher_message(messages[idx])
        else:
            st.session_state.show_all_messages = True
            st.session_state.message_index = -1
            st.rerun()

    # Barre de navigation
    if total > 1:
        st.markdown("---")
        if st.session_state.show_all_messages:
            if st.button("🔍 Naviguer dans les messages (un par un)", use_container_width=True):
                st.session_state.show_all_messages = False
                st.session_state.message_index = total - 1
                st.rerun()
        else:
            col_prev, col_info, col_next, col_back = st.columns([1, 2, 1, 2])
            with col_prev:
                if st.button("◀️ Précédent", use_container_width=True, disabled=(st.session_state.message_index <= 0)):
                    st.session_state.message_index -= 1
                    st.rerun()
            with col_info:
                st.markdown(f"<p style='text-align:center; margin:0; font-weight:500;'>Message {st.session_state.message_index+1} / {total}</p>", unsafe_allow_html=True)
            with col_next:
                if st.button("Suivant ▶️", use_container_width=True, disabled=(st.session_state.message_index >= total-1)):
                    st.session_state.message_index += 1
                    st.rerun()
            with col_back:
                if st.button("📋 Voir tous les messages", use_container_width=True):
                    st.session_state.show_all_messages = True
                    st.session_state.message_index = -1
                    st.rerun()

# ==================== PAGE D'ACCUEIL (BENTO GRID) ====================
if len(st.session_state.messages) == 0:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#3B82F6; font-weight:600; font-size:14px;'>Welcome to BI Chatbot Pro</p>", unsafe_allow_html=True)
    st.markdown("<h1 class='hero-title'>Bonjour ! je suis votre assistant IA. Comment puis-je vous aider ?</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    CARDS = [
        {"title": "📊 Volume Global", "desc": "Déterminez le nombre exact de clients ou de commandes.",
         "question": "Donne-moi le nombre total de clients et le nombre total de commandes."},
        {"title": "🏆 Top Performances", "desc": "Trouvez la référence produit ou la marque la plus vendue.",
         "question": "Quels sont les 10 produits les plus vendus ?"},
        {"title": "🎯 Profils Clients", "desc": "Analysez la répartition des acheteurs par ville ou sexe.",
         "question": "Affiche la répartition des clients par sexe et par pays."},
        {"title": "💸 Analyse CA & Marge", "desc": "Calculez les profits et observez l'impact des remises.",
         "question": "Calcule le chiffre d'affaires total, le profit total et la marge moyenne."}
    ]

    cols = st.columns(4)
    for idx, card in enumerate(CARDS):
        with cols[idx]:
            label = f"**{card['title']}**\n\n{card['desc']}"
            if st.button(label, key=f"bento_{idx}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": card["question"]})
                st.session_state.show_all_messages = True
                st.session_state.message_index = -1
                st.rerun()

    # CSS pour les boutons Bento
    st.markdown("""
    <style>
        .stButton > button {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 16px !important;
            padding: 20px !important;
            min-height: 140px !important;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03) !important;
            transition: all 0.2s ease-in-out !important;
            position: relative !important;
            overflow: hidden !important;
            text-align: left !important;
            font-weight: normal !important;
            color: #1E293B !important;
            width: 100% !important;
            height: auto !important;
            white-space: normal !important;
            line-height: 1.5 !important;
            font-size: 14px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: flex-start !important;
            cursor: pointer !important;
        }
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1) !important;
            border-color: #CBD5E1 !important;
        }
        .stButton > button::before {
            content: "" !important;
            position: absolute !important;
            top: 0 !important; left: 0 !important; right: 0 !important;
            height: 5px !important;
            border-radius: 16px 16px 0 0 !important;
        }
        #bento_0::before { background: linear-gradient(90deg, #4ADE80, #22C55E) !important; }
        #bento_1::before { background: linear-gradient(90deg, #60A5FA, #3B82F6) !important; }
        #bento_2::before { background: linear-gradient(90deg, #C084FC, #A855F7) !important; }
        #bento_3::before { background: linear-gradient(90deg, #FB923C, #F97316) !important; }
        .stButton > button strong {
            font-size: 16px !important;
            font-weight: 600 !important;
            margin-bottom: 4px !important;
            display: block !important;
        }
        .stButton > button p {
            margin: 0 !important;
            color: #64748B !important;
            font-size: 13px !important;
        }
    </style>
    """, unsafe_allow_html=True)

# ==================== ZONE DE SAISIE ====================
if st.session_state.application_active:
    st.markdown("""
    <div style='display:flex; gap:8px; margin-bottom:-10px; justify-content:center;'>
        <span style='background:#E2E8F0; color:#475569; font-size:11px; padding:4px 12px; border-radius:20px; font-weight:500;'>⚡ Fast Mode (Groq)</span>
        <span style='background:#E2E8F0; color:#475569; font-size:11px; padding:4px 12px; border-radius:20px; font-weight:500;'>🔍 Deep SQL Check</span>
        <span style='background:#E2E8F0; color:#475569; font-size:11px; padding:4px 12px; border-radius:20px; font-weight:500;'>🕒 Session Tracker</span>
    </div>
    """, unsafe_allow_html=True)

    question_utilisateur = st.chat_input("Posez votre question...")
    if question_utilisateur:
        st.session_state.messages.append({"role": "user", "content": question_utilisateur})
        st.session_state.show_all_messages = True
        st.session_state.message_index = -1
        st.rerun()

# ==================== TRAITEMENT DE L'ASSISTANT ====================
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and st.session_state.application_active:
    with st.chat_message("assistant", avatar="🔵"):
        with st.spinner("🤖 Réflexion de l'assistant Groq..."):
            try:
                debut_llm = time.time()
                reponse_structuree = generer_requete_sql(st.session_state.messages)
                fin_llm = time.time()

                if not isinstance(reponse_structuree, dict):
                    raise Exception(f"Réponse inattendue du LLM : {type(reponse_structuree)}")

                requete_sql = reponse_structuree.get("sql")
                phrase_commentaire = reponse_structuree.get("commentaire", "Voici les résultats :")

                if requete_sql:
                    requete_sql = requete_sql.strip().rstrip(";")
                    # Sécurité : Forcer ILIKE pour PostgreSQL si nécessaire
                    requete_sql = re.sub(r"\bmarque\s+LIKE\b", "marque ILIKE", requete_sql, flags=re.IGNORECASE)

                    valide, erreur_validation = valider_requete_sql(requete_sql)
                    if not valide:
                        raise Exception(f"Validation SQL échouée : {erreur_validation}")

                    # Protection contre les tables trop volumineuses (limite par défaut si pas d'agrégation)
                    mots_cles_agreg = ["SUM(", "COUNT(", "AVG(", "MIN(", "MAX("]
                    if "LIMIT" not in requete_sql.upper() and not any(x in requete_sql.upper() for x in mots_cles_agreg):
                        requete_sql += " LIMIT 100"

                    debut_sql = time.time()

                    # Système de cache local pour éviter les requêtes DB identiques successives
                    sql_hash = hashlib.md5(requete_sql.encode()).hexdigest()
                    if sql_hash in st.session_state.sql_cache:
                        df_resultat = st.session_state.sql_cache[sql_hash]
                        st.info("📦 Résultat récupéré depuis le cache.")
                    else:
                        with engine.connect() as conn:
                            result = conn.execute(text(requete_sql))
                            cols = result.keys()
                            rows = result.fetchall()
                            df_resultat = pd.DataFrame(rows, columns=cols)
                        df_resultat = deduplicate_columns(df_resultat)
                        st.session_state.sql_cache[sql_hash] = df_resultat

                    fin_sql = time.time()

                    txt_performance = (
                        f"Génération SQL (Groq) : {round(fin_llm - debut_llm, 2)}s | "
                        f"Base de données : {round(fin_sql - debut_sql, 2)}s."
                    )

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": phrase_commentaire,
                        "is_sql": True,
                        "df_resultat": df_resultat,
                        "query_sql": requete_sql,
                        "analytics_text": txt_performance,
                        "status_ok": True
                    })
                else:
                    # Cas où l'assistant répond directement par du texte sans code SQL généré
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": phrase_commentaire,
                        "is_sql": False,
                        "status_ok": True
                    })
                st.rerun()

            except Exception as e:
                # Gestion propre des anomalies et affichage direct de l'erreur dans le flux
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "⚠️ Une erreur est survenue lors de l'exécution de votre demande.",
                    "is_sql": False,
                    "analytics_text": str(e),
                    "status_ok": False
                })
                st.rerun()