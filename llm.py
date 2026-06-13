# llm.py
# Fichier situé à la racine : C:\Users\Bahissou TCHAGNAO\Desktop\Chatbot_project\Chatbot_data_science\llm.py

import os
import json
from openai import OpenAI
from prompts import PROMPT_SYSTEME  # Importation du prompt depuis ton nouveau fichier prompts.py

def generer_requete_sql(messages_historique):
    """
    Analyse l'historique de discussion avec DeepSeek-Coder via son API officielle
    et renvoie un dictionnaire JSON structuré.
    """
    # Initialisation du client officiel DeepSeek
    # Pense à remplacer "ta_cle_api_ici" par ta vraie clé DeepSeek (ex: sk-...) si tu ne passes pas par les variables d'environnement
    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY", "ta_cle_api_ici"),
        base_url="https://api.deepseek.com/v1"
    )
    
    # Préparation du format des messages pour DeepSeek
    messages = [{"role": "system", "content": PROMPT_SYSTEME}]
    
    # Adaptation de l'historique de Streamlit pour l'API DeepSeek
    for msg in messages_historique:
        role = msg["role"]
        if role == "model":  # Gestion du renommage si Streamlit utilise 'model' au lieu de 'assistant'
            role = "assistant"
        messages.append({
            "role": role,
            "content": str(msg["content"])
        })
        
    try:
        # Appel du modèle cloud spécialisé de DeepSeek
        response = client.chat.completions.create(
            model="deepseek-coder",
            messages=messages,
            temperature=0.1,  # Très basse pour éviter les dérives de syntaxe SQL
            response_format={
                'type': 'json_object'  # Demande nativement à DeepSeek de structurer sa réponse en JSON
            }
        )
        
        # Extraction et décodage sécurisés du JSON
        texte_reponse = response.choices[0].message.content
        return json.loads(texte_reponse)
        
    except Exception as e:
        # Fallback propre pour ne pas faire planter app.py en cas d'erreur réseau/clé API
        return {
            "sql": None,
            "commentaire": f"Désolé Bahissou, je rencontre des difficultés techniques avec l'API DeepSeek-Coder. (Détails : {str(e)})"
        }