import pandas as pd
from sqlalchemy import create_engine
import urllib.parse

# 1. Encodage sécurisé du mot de passe pour PostgreSQL
password = urllib.parse.quote_plus("Bahiss@u02gnao")

# 2. Création du moteur de connexion (le pont Python-PostgreSQL)
engine = create_engine(
    f"postgresql://postgres:{password}@localhost:5432/chatbot_db"
)

# 3. Requête SQL de test : demander les 5 premiers clients
query = "SELECT * FROM clients LIMIT 5"

# 4. Pandas exécute la requête via le moteur et stocke le résultat
df = pd.read_sql(query, engine)

# 5. Affichage du tableau dans le terminal
print(df)