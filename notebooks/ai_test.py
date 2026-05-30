import ollama
import pandas as pd
from sqlalchemy import create_engine
import urllib.parse

# 1. Connexion sécurisée à votre base PostgreSQL
password = urllib.parse.quote_plus("Bahiss@u02gnao")
engine = create_engine(f"postgresql://postgres:{password}@localhost:5432/chatbot_db")

# 2. Le plan de votre base de données (Le Contexte)
prompt_systeme = """
Tu es un moteur Text-to-SQL pour PostgreSQL. Tu dois répondre UNIQUEMENT avec la requête SQL brute, sans explications, sans politesse et sans balises Markdown.
Si la question de l'utilisateur n'a aucun rapport avec la base de données ou ne veut rien dire, réponds exactement : "ERREUR: Question invalide."

Tu travailles avec une base PostgreSQL contenant les tables suivantes :

TABLE clients
- id_client, age_client, ville_client, pays_client, code_iso_client, sexe_client, nom_client

TABLE produits
- id_produit, nom_produit, categorie, sous_categorie, marque

TABLE magasins
- id_magasin, nom_magasin, ville_magasin, pays_magasin, continent_magasin, code_iso_magasin

TABLE commandes
- id_commande, date_commande, id_client, id_magasin, methode_paiement, mode_livraison

TABLE ventes
- id_commande, id_produit, quantite, prix_unitaire, remise, montant_ventes, profit, stock_disponible

Relations (JOINTURES OBLIGATOIRES si tu utilises plusieurs tables) :
- ventes.id_commande = commandes.id_commande
- ventes.id_produit = produits.id_produit
- commandes.id_client = clients.id_client
- commandes.id_magasin = magasins.id_magasin

Tu devez générer uniquement du SQL PostgreSQL valide.
Tu ne dois jamais faire des explications, ni donner des conseils, ni faire du storytelling. 
Tu dois répondre uniquement avec la requête SQL brute, sans explications, sans politesse et sans balises Markdown.
Si la question de l'utilisateur n'a aucun rapport avec la base de données ou ne veut rien dire,
réponds exactement : "ERREUR: Question invalide."
Donneuniquament la réponse à  la question posée, sans rien ajouter d'autre.

"""

# 3. Entrée interactive pour l'utilisateur
question_utilisateur = input("Posez une question : ")

# 4. Historique de discussion optimisé (Les 4 exemples stratégiques)
historique_discussion = [
    {'role': 'system', 'content': prompt_systeme},
    
    # Structure 1 : Agrégation simple sur une table
    {'role': 'user', 'content': "Combien de clients avons-nous dans la base ?"},
    {'role': 'assistant', 'content': "SELECT COUNT(*) FROM clients;"},
    
    # Structure 2 : Filtrage, Tri et Limite
    {'role': 'user', 'content': "Quels sont les 5 magasins les plus récents au niveau de leur id ?"},
    {'role': 'assistant', 'content': "SELECT nom_magasin FROM magasins ORDER BY id_magasin DESC LIMIT 5;"},
    
    # Structure 3 : Jointure double (Ventes -> Produits) avec somme
    {'role': 'user', 'content': "Quel est le produit le plus vendu ?"},
    {'role': 'assistant', 'content': "SELECT p.nom_produit, SUM(v.quantite) AS total_vendu FROM ventes v JOIN produits p ON v.id_produit = p.id_produit GROUP BY p.nom_produit ORDER BY total_vendu DESC LIMIT 1;"},
    
    # Structure 4 : Jointure triple complexe (Ventes -> Commandes -> Magasins) avec filtre temporel
    {'role': 'user', 'content': "Quel est le montant des ventes réalisées à Paris en 2025 ?"},
    {'role': 'assistant', 'content': "SELECT SUM(v.montant_ventes) FROM ventes v JOIN commandes c ON v.id_commande = c.id_commande JOIN magasins m ON c.id_magasin = m.id_magasin WHERE m.ville_magasin = 'Paris' AND c.date_commande BETWEEN '2025-01-01' AND '2025-12-31';"},
    
    # Injection de votre question
    {'role': 'user', 'content': question_utilisateur}
]

# 5. Envoi à l'IA et nettoyage du résultat
reponse = ollama.chat(model='mistral', messages=historique_discussion)
requete_sql = reponse['message']['content'].strip()

# 6. Sécurité : On vérifie si c'est du SQL avant d'interroger PostgreSQL
if "ERREUR" in requete_sql or not requete_sql.upper().startswith("SELECT"):
    print("\n🤖 Le chatbot n'a pas pu traiter votre demande.")
    print("Raison : La question doit être une demande de données claire.")
else:
    print(f"\n[SQL exécuté] : {requete_sql}\n")
    try:
        df_resultat = pd.read_sql(requete_sql, engine)
        print("[Réponse] :")
        print(df_resultat)
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution du SQL : {e}")