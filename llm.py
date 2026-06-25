import streamlit as st
import json
from openai import OpenAI
from prompts import PROMPT_SYSTEME

def generer_requete_sql(messages_historique):
    """
    Analyse l'historique de discussion avec le modèle via l'API de Groq
    et renvoie un dictionnaire JSON structuré.
    """
    client = OpenAI(
        api_key=st.secrets["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1"
    )
    
    messages = [{"role": "system", "content": PROMPT_SYSTEME}]
    
    for msg in messages_historique:
        role = msg["role"]
        if role == "model" or role == "assistant":
            role = "assistant"
        messages.append({
            "role": role,
            "content": str(msg["content"])
        })
    
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            temperature=0.1,
            response_format={'type': 'json_object'}
        )
        
        texte_reponse = response.choices[0].message.content
        return json.loads(texte_reponse)
    
    except Exception as e:
        return {
            "sql": None,
            "commentaire": f"Erreur technique : {str(e)}"
        }