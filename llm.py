# llm.py
# Fichier situé à la racine : C:\Users\Bahissou TCHAGNAO\Desktop\Chatbot_project\Chatbot_data_science\llm.py

import streamlit as st  
import json
from openai import OpenAI
from prompts import PROMPT_SYSTEME

def generer_requete_sql(messages_historique):
    """
    Analyse l'historique de discussion avec Llama-3 via l'API de Groq
    et renvoie un dictionnaire JSON structuré.
    """
    # Configuration pour pointer vers les serveurs gratuits de Groq
    client = OpenAI(
        api_key=st.secrets["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1"
    )
    
    # Préparation du format des messages
    messages = [{"role": "system", "content": PROMPT_SYSTEME}]
    
    # Adaptation de l'historique de Streamlit
    for msg in messages_historique:
        role = msg["role"]
        if role == "model":  
            role = "assistant"
        messages.append({
            "role": role,
            "content": str(msg["content"])
        })
        
    try:
        # Appel du puissant modèle de Meta (Llama 3) hébergé par Groq
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Modèle gratuit et ultra-rapide
            messages=messages,
            temperature=0.1,  
            response_format={
                'type': 'json_object'  # Demande une réponse structurée en JSON
            }
        )
        
        # Extraction et décodage sécurisés du JSON
        texte_reponse = response.choices[0].message.content
        return json.loads(texte_reponse)
        
    except Exception as e:
        return {
            "sql": None,
            "commentaire": f"Désolé Bahissou, je rencontre des difficultés techniques avec l'API Groq. (Détails : {str(e)})"
        }