import re

MOTS_CLES_INTERDITS = [
    "DROP", "DELETE", "TRUNCATE", "ALTER", "UPDATE",
    "INSERT", "GRANT", "REVOKE", "CREATE", "MERGE"
]

MOTS_CLES_AUTORISES = [
    "SELECT", "FROM", "WHERE", "JOIN", "ON", 
    "GROUP BY", "ORDER BY", "HAVING", "LIMIT", 
    "SUM", "COUNT", "AVG", "MIN", "MAX", "DISTINCT",
    "WITH", "CASE", "WHEN", "THEN", "ELSE", "END",
    "ILIKE", "AS", "IN", "EXISTS", "NOT", "AND", "OR"
]

def valider_requete_sql(query: str) -> tuple[bool, str]:
    if not query or not query.strip():
        return False, "La requête générée est vide."

    query_upper = query.upper()
    
    # Interdire les multiples points-virgules (injection)
    if query_upper.count(';') > 1:
        return False, "Requête contenant plusieurs instructions interdites."

    # Vérifier les mots-clés interdits
    for mot in MOTS_CLES_INTERDITS:
        if re.search(r'\b' + mot + r'\b', query_upper):
            return False, f"Action non autorisée : '{mot}' détecté."

    # Vérifier le début de la requête principale
    debut = query_upper.lstrip()
    if not (debut.startswith("SELECT") or debut.startswith("WITH")):
        return False, "La requête doit commencer par SELECT ou WITH."

    return True, "Requête sécurisée."