
import pandas as pd
# Charger les données
df = pd.read_csv("../data/chatbot_data.csv")

print("\n===== APERÇU =====")
print(df.head())

print("\n===== COLONNES =====")
print(df.columns)

print("\n===== TYPES =====")
print(df.info())
print("\n===== VALEURS MANQUANTES =====")
print(df.isnull().sum())
print("\n===== STATISTIQUES =====")
print(df.describe())

