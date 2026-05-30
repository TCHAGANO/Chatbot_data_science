## Bilan de la phase de préparation des données et de l’infrastructure du projet

À ce stade du projet, une grande partie des fondations techniques nécessaires au développement du chatbot intelligent a été mise en place. L’objectif principal de cette phase n’était pas encore de construire l’intelligence artificielle elle-même, mais plutôt de préparer une architecture de données solide, stable et professionnelle capable de supporter les futures analyses et interactions du chatbot.

### 1) Préparation de l’environnement de travail

La première étape du projet a consisté à préparer l’environnement Python nécessaire au développement. Plusieurs bibliothèques fondamentales ont été installées afin de couvrir les besoins liés à la manipulation des données, au stockage SQL, à la génération de données fictives ainsi qu’à la future interface utilisateur.

Les bibliothèques installées sont :

```python
pip install pandas numpy faker sqlalchemy psycopg2 streamlit
```

Chaque bibliothèque possède un rôle spécifique :

* Pandas : manipulation et analyse des données
* NumPy : calculs numériques
* Faker : génération de données fictives réalistes
* SQLAlchemy : communication entre Python et PostgreSQL
* psycopg2 : connexion PostgreSQL
* Streamlit : future interface web du chatbot

Durant cette phase, la notion de Framework a également été étudiée. Un framework peut être vu comme une structure déjà préparée permettant de développer une application plus rapidement et de manière organisée. Cette compréhension est importante car le projet utilisera plusieurs outils fonctionnant selon cette logique architecturale.

---

### 2) Génération du dataset principal

Une fois l’environnement prêt, un script Python nommé :

```python
generate_chatbot_data.py
```

a été créé afin de générer automatiquement un dataset volumineux simulant l’activité d’une entreprise internationale.

Pour accélérer la création de la logique métier et structurer correctement les données, l’intelligence artificielle DeepSeek a été utilisée comme assistant de génération de code. L’objectif n’était pas de copier aveuglément le code généré, mais plutôt de comprendre son fonctionnement puis l’adapter aux besoins réels du projet.

Le script produit un fichier :

```python
chatbot_data.csv
```

contenant environ 500 000 lignes de données simulées.

Le dataset inclut notamment :

* clients
* produits
* fournisseurs
* magasins
* commandes
* ventes
* paiements
* livraisons

Une attention particulière a été portée à la personnalisation des données. Certains profils spécifiques ont été ajoutés afin de simuler des comportements réalistes, notamment des clients VIP effectuant des volumes d’achats très élevés. Cette approche permettra plus tard de tester les capacités d’analyse du chatbot et des requêtes SQL.

Le script contient également une logique de renommage automatique des colonnes afin d’obtenir des noms cohérents directement en français. Cette étape facilite ensuite la création des tables SQL et améliore la lisibilité générale du projet.

---

### 3) Analyse exploratoire des données (EDA)

Avant de créer la base SQL, une phase d’analyse exploratoire des données a été réalisée dans un fichier :

```python
analysis.py
```

situé dans le dossier :

```python
notebooks/
```

L’objectif était de comprendre précisément la structure du dataset avant toute modélisation relationnelle.

Plusieurs opérations ont été effectuées :

* affichage des premières lignes
* vérification des types de données
* recherche de valeurs manquantes
* analyse statistique descriptive
* inspection des colonnes
* validation de la cohérence globale des données

Cette étape est essentielle car une mauvaise compréhension des données au départ peut provoquer de nombreuses erreurs plus tard lors de la création de la base SQL ou des modèles d’intelligence artificielle.

---

### 4) Transformation du CSV vers une base relationnelle SQL

Le fichier CSV généré contenait initialement toutes les informations dans une seule grande table. Cette structure n’était pas optimale pour les futures analyses ni pour les performances du chatbot.

Pour résoudre ce problème, une base PostgreSQL nommée :

```sql
chatbot_db
```

a été créée dans pgAdmin 4.

Le dataset a ensuite été normalisé afin de répartir les informations dans plusieurs tables relationnelles reliées entre elles grâce aux clés primaires et étrangères.

Les principales tables créées sont :

* clients
* produits
* magasins
* commandes
* ventes

Cette normalisation permet :

* d’éviter les duplications
* d’améliorer les performances SQL
* de simplifier les analyses
* de préparer les futures requêtes du chatbot

Le chatbot ne travaillera donc pas directement sur un fichier CSV massif, mais sur une base relationnelle optimisée.

---

### 5) Création du pipeline automatique d’injection SQL

Un script Python nommé :

```python
load_data.py
```

a ensuite été développé afin d’automatiser complètement le chargement des données du CSV vers PostgreSQL.

Ce script réalise plusieurs opérations importantes :

* connexion automatique à PostgreSQL
* nettoyage des tables avec TRUNCATE
* conversion des dates au bon format
* extraction des colonnes nécessaires
* insertion des données dans chaque table via SQLAlchemy

Plusieurs difficultés techniques ont été rencontrées durant cette étape.

Par exemple, certaines erreurs provenaient du fait que les noms des colonnes du CSV avaient changé après le renommage automatique. Le script SQL recherchait encore les anciens noms de colonnes, ce qui provoquait des erreurs de type :

```python
KeyError: 'id_pays_client'
```

Le problème a été résolu en synchronisant les noms de colonnes entre :

* le fichier CSV
* le script rename_columns.py
* le script load_data.py

Une fois ces corrections effectuées, les données ont été injectées avec succès dans PostgreSQL sans erreur.

---

### 6) Gestion professionnelle du projet avec Git et GitHub

Afin de sécuriser le projet et suivre toutes les modifications, Git et GitHub ont été utilisés dès le début du développement.

Une architecture basée sur deux branches a été mise en place :

* main : version stable
* dev : environnement de développement

Cette séparation permet de travailler librement sur de nouvelles fonctionnalités sans risquer de casser la version principale du projet.

Les principales commandes Git utilisées durant cette phase sont :

```bash
git init
git status
git add .
git commit -m "message"
git push origin dev
git checkout main
git merge dev
```

---

### 7) Difficultés Git avancées rencontrées

La principale difficulté Git rencontrée concernait la taille du fichier :

```python
chatbot_data.csv
```

GitHub impose une limite de 100 MB par fichier, tandis que le dataset généré dépassait cette limite.

Même après suppression du fichier, GitHub refusait encore le push car le CSV existait toujours dans l’historique des commits.

Pour résoudre ce problème, il a fallu effectuer un nettoyage avancé de l’historique Git avec des commandes comme :

```bash
git filter-branch
git gc --prune=now
```

Cette étape a permis de supprimer définitivement le gros fichier de l’historique du dépôt.

Une autre difficulté est apparue lors de la synchronisation entre les branches locales et distantes :

```bash
fatal: refusing to merge unrelated histories
```

Cette erreur provenait des modifications profondes apportées à l’historique Git après réécriture des commits. Le problème a finalement été résolu grâce à une fusion correcte entre les branches `dev` et `main`.

---

## Situation actuelle du projet

À ce stade, toute l’infrastructure de données du projet est maintenant opérationnelle.

Le pipeline complet fonctionne correctement :

* génération des données
* analyse exploratoire
* normalisation SQL
* création des tables
* chargement automatique PostgreSQL
* gestion Git/GitHub

Le projet dispose désormais d’une base technique solide et stable.

La prochaine grande étape consistera à développer le moteur d’intelligence artificielle du chatbot afin de permettre :

* l’interrogation intelligente des données
* les requêtes SQL automatiques
* les réponses conversationnelles
* l’analyse métier automatisée

Cette transition marque le passage entre la phase d’ingénierie des données et la phase d’intelligence artificielle du projet.
