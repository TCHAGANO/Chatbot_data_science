# llm.py

import ollama
from prompts import PROMPT_SYSTEME

def generer_requete_sql(messages_session):
    """
    Analyse l'intention. Si l'utilisateur demande une analyse textuelle ou 
    fait une relance ouverte, on retourne un commentaire. Sinon, du SQL strict.
    """
    messages_pipeline = [{'role': 'system', 'content': PROMPT_SYSTEME}]
    
    # On passe l'historique converti pour Ollama
    for msg in messages_session:
        messages_pipeline.append({
            'role': msg['role'],
            'content': msg['content']
        })
        
    reponse = ollama.chat(
        model='mistral',
        messages=messages_pipeline,
        options={"temperature": 0.1, "num_predict": 256}
    )
    
    texte_brut = reponse['message']['content'].strip()
    
    # Nettoyage si le modèle a quand même mis des balises markdown
    texte_nettoye = texte_brut.replace("```sql", "").replace("```", "").strip()
    
    return texte_nettoye