import re

# Liste des mots-clés SQL strictement interdits en lecture seule Business Intelligence
MOTS_CLES_INTERDITS = [
    "DROP", "DELETE", "TRUNCATE", "ALTER", "UPDATE", 
    "INSERT", "GRANT", "REVOKE", "CREATE TABLE"
]

def valider_requete_sql(query: str) -> tuple[bool, str]:
    """
    Analyse la requête SQL générée par l'IA pour s'assurer qu'elle est 
    strictement limitée à de la lecture de données (SELECT).
    """
    if not query:
        return False, "La requête générée est vide."
        
    query_upper = query.upper()
    
    # 1. Vérification des mots-clés interdits
    for mot in MOTS_CLES_INTERDITS:
        # Le \b assure qu'on cherche le mot exact (ex: pas bloquer le mot 'UPDATED_AT')
        if re.search(r'\b' + mot + r'\b', query_upper):
            return False, f"Action non autorisée détectée : Utilisation du mot-clé interdit '{mot}'."
    
    # 2. Vérification que la requête commence bien par une lecture
    if not query_upper.strip().startswith("SELECT") and not query_upper.strip().startswith("WITH"):
        return False, "Requête invalide : Les requêtes doivent impérativement commencer par SELECT ou WITH."
        
    return True, "Requête sécurisée."