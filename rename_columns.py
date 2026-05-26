import pandas as pd

data = pd.read_csv(
r"C:\Users\Bahissou TCHAGNAO\Desktop\Chatbot_project\chatbot_data.csv"
)

data=data.rename(columns={

"order_id":"id_commande",
"order_date":"date_commande",

"client_id":"id_client",
"client_name":"nom_client",
"client_age":"age_client",
"client_gender":"sexe_client",
"client_city":"ville_client",

"client_country_name":"pays_client",
"client_phone_code":"code_iso_client",

"store_country_name":"pays_magasin",
"store_continent":"continent_magasin",
"store_phone_code":"code_iso_magasin",

"store_id":"id_magasin",
"store_name":"nom_magasin",
"store_city":"ville_magasin",

"product_id":"id_produit",
"product_name":"nom_produit",
"category":"categorie",
"subcategory":"sous_categorie",
"brand":"marque",

"supplier_id":"id_fournisseur",
"supplier_name":"nom_fournisseur",

"quantity":"quantite",
"unit_price":"prix_unitaire",
"discount":"remise",
"sales_amount":"montant_ventes",
"stock_quantity":"stock_disponible",

"payment_method":"methode_paiement",
"shipping_mode":"mode_livraison"

})

data.to_csv(
r"C:\Users\Bahissou TCHAGNAO\Desktop\Chatbot_project\chatbot_data.csv",
index=False
)

print("Colonnes renommées")
print(data.columns.tolist())