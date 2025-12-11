# Application de Gestion du Parrainage - Keyce Informatique

Ce projet est une application web pour gérer le processus de parrainage des étudiants à Keyce Informatique. Il se compose d'un backend en Python (Flask) et d'un frontend en HTML, CSS et JavaScript.

## Prérequis

-   [Python 3.10+](https://www.python.org/downloads/)
-   `pip` (généralement inclus avec Python)
-   Un navigateur web moderne (Chrome, Firefox, Edge, etc.)

## Installation et Lancement

Le projet est divisé en deux parties : le backend (serveur) et le frontend (interface utilisateur). Ils doivent être lancés séparément.

### 1. Backend (Serveur Flask)

Le backend gère la logique de l'application, la base de données et l'algorithme de parrainage.

Ouvrez un terminal ou une invite de commande et suivez ces étapes :

```bash
# 1. Clonez le projet ou naviguez vers le répertoire du projet.
# cd ParrainageApp

# 2. Naviguez vers le dossier du backend
cd backend

# 3. Créez un environnement virtuel Python
# Sur Windows:
python -m venv venv

# Sur macOS/Linux:
# python3 -m venv venv

# 4. Activez l'environnement virtuel
# Sur Windows:
virtualenv\Scripts\activate

# Sur macOS/Linux:
# source venv/bin/activate

# 5. Installez les dépendances
pip install -r requirements.txt

# 6. Initialisez la base de données
# Cette commande crée le fichier parrainage.db et remplit la table des promotions.
flask init-db

# 7. Lancez le serveur Flask
# Le serveur sera accessible à l'adresse http://127.0.0.1:5000
flask run
```

Laissez ce terminal ouvert. Le serveur doit continuer de tourner pour que l'application fonctionne.

### 2. Frontend (Interface Cérémonie)

Le frontend est l'interface visuelle que vous utiliserez pendant la cérémonie.

1.  Ouvrez votre explorateur de fichiers.
2.  Naviguez vers le dossier `frontend`.
3.  Double-cliquez sur le fichier `index.html` pour l'ouvrir dans votre navigateur web par défaut.

L'application est maintenant prête à être utilisée !

## Utilisation

L'interface web présente plusieurs boutons :

-   **Importer**: Lit le fichier `backend/data/students.csv` et remplit la base de données avec la liste des étudiants. **Attention :** cette action efface toutes les données existantes (étudiants et paires).
-   **Exporter CSV**: Télécharge un fichier CSV contenant la liste de toutes les paires qui ont été formées.
-   **Annuler**: Annule le dernier tirage effectué, rendant le parrain et le filleul de nouveau disponibles.
-   **Réinitialiser**: Supprime toutes les paires formées et réinitialise le statut de tous les étudiants, sans supprimer les étudiants de la base de données.
-   **Lancer le Tirage**: Bouton principal qui exécute l'algorithme pour former une nouvelle paire parrain-filleul.

Les compteurs en bas de page indiquent le nombre de parrains potentiels et le nombre de filleuls qui n'ont pas encore été assignés.