import pandas as pd
from sqlalchemy import create_engine, text
import urllib.parse

try:
    # 1. Lecture du fichier CSV global
    csv_path = r"C:\Users\Bahissou TCHAGNAO\Desktop\Chatbot_project\Chatbot_data_science\chatbot_data.csv"
    print("🔄 Lecture du dataset CSV...")
    df = pd.read_csv(csv_path, dtype=str)

    # 2. Connexion PostgreSQL (LIGNE MODIFIÉE ICI POUR NEON CLOUD)
    engine = create_engine("postgresql://neondb_owner:npg_DIa8Lj4OifuZ@ep-autumn-dust-at2s18do-pooler.c-9.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")
    print("✅ Connexion à NEON CLOUD établie avec succès !")

    # 4. Extraction et injection
    print("\n✂️ Extraction et injection des données...")

    # --- TABLE CLIENTS ---
    print("-> Remplissage de la table 'clients'...")
    df_clients = df[[
        'id_client', 'nom_client', 'age_client', 'sexe_client', 'ville_client', 'pays_client', 'code_iso_client'
    ]].drop_duplicates()
    df_clients.to_sql("clients", engine, if_exists="append", index=False)

    # --- TABLE PRODUITS ---
    print("-> Remplissage de la table 'produits'...")
    df_produits = df[[
        'id_produit', 'nom_produit', 'categorie', 'sous_categorie', 'marque', 'id_fournisseur', 'nom_fournisseur'
    ]].drop_duplicates()
    df_produits.to_sql("produits", engine, if_exists="append", index=False)

    # --- TABLE MAGASINS ---
    print("-> Remplissage de la table 'magasins'...")
    df_magasins = df[[
        'id_magasin', 'nom_magasin', 'ville_magasin', 'pays_magasin', 'continent_magasin', 'code_iso_magasin'
    ]].drop_duplicates()
    df_magasins.to_sql("magasins", engine, if_exists="append", index=False)

    # --- TABLE COMMANDES ---
    print("-> Remplissage de la table 'commandes'...")
    df_commandes = df[[
        'id_commande', 'date_commande', 'id_client', 'id_magasin', 'methode_paiement', 'mode_livraison'
    ]].drop_duplicates()
    
    # ÉVITE LE BUG DES DATES : On spécifie explicitement le format jj/mm/aaaa
    df_commandes['date_commande'] = pd.to_datetime(df_commandes['date_commande'], format='%d/%m/%Y')
    
    df_commandes.to_sql("commandes", engine, if_exists="append", index=False)

    # --- TABLE VENTES ---
    print("-> Remplissage de la table 'ventes'...")
    df_ventes = df[[
        'id_commande', 'id_produit', 'quantite', 'prix_unitaire', 'remise', 'montant_ventes', 'profit', 'stock_disponible'
    ]].drop_duplicates()
    df_ventes.to_sql("ventes", engine, if_exists="append", index=False)

    print("\n🎉 TOUTES LES TABLES ONT ÉTÉ SYNCHRONISÉES ET REMPLIES AVEC SUCCÈS SUR NEON !")

except Exception as e:
    print("\n❌ Une erreur est survenue lors du chargement :")
    print(e)