import re

MOTS_CLES_INTERDITS = [
    "DROP", "DELETE", "TRUNCATE", "ALTER", "UPDATE",
    "INSERT", "GRANT", "REVOKE", "CREATE", "MERGE"
]

def valider_requete_sql(query: str) -> tuple[bool, str]:
    if not query or not query.strip():
        return False, "La requête générée est vide."

    query_upper = query.upper()
    
    # Interdire les multiples points-virgules (injection stacking)
    if query_upper.count(';') > 1:
        return False, "Requête contenant plusieurs instructions interdites."

    # Vérifier les mots-clés interdits (en évitant les chaînes de caractères – simplifié)
    # Une amélioration serait de retirer les chaînes entre quotes avant analyse, mais plus complexe.
    for mot in MOTS_CLES_INTERDITS:
        if re.search(r'\b' + mot + r'\b', query_upper):
            return False, f"Action non autorisée : '{mot}' détecté."

    # Vérifier le début de la requête principale (on enlève les espaces)
    debut = query_upper.lstrip()
    if not (debut.startswith("SELECT") or debut.startswith("WITH")):
        return False, "La requête doit commencer par SELECT ou WITH."

    return True, "Requête sécurisée."