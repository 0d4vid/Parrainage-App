# Documentation du Projet : Application de Gestion du Parrainage

Ce document décrit l'architecture, la structure et les étapes de développement pour la création de l'application de gestion du parrainage pour Keyce Informatique, en se basant sur le cahier des charges fourni.

## 1. Vue d'ensemble du Projet

L'objectif est de développer une application web locale pour gérer l'attribution de parrains et de filleuls parmi les étudiants de Keyce Informatique. L'application doit non seulement automatiser le processus de tirage en respectant des règles précises, mais aussi offrir une interface visuelle et animée pour la "Cérémonie de Parrainage".

Les fonctionnalités clés incluent :
- **Gestion des données** : Import/export de listes d'étudiants (CSV), nettoyage des données.
- **Algorithme de parrainage** : Tirage aléatoire, gestion des déséquilibres, équilibrage des attributions.
- **Interface de cérémonie** : Affichage plein écran, animations visuelles pour la mise en relation.
- **Administration** : Possibilité de réinitialiser le tirage et d'annuler la dernière attribution.

## 2. Architecture Technique

Conformément aux spécifications, nous adoptons une architecture client-serveur locale :

*   **Backend (Logique Métier)** : **Python** avec le micro-framework **Flask**.
    *   **Rôle** : Gérer la base de données, implémenter l'algorithme de parrainage, et exposer une API REST pour que le frontend puisse communiquer avec le serveur.
    *   **Librairies** : `Flask`, `Flask-SQLAlchemy` (pour l'interaction avec la base de données), `Pandas` (pour l'import/export CSV).

*   **Frontend (Interface Visuelle)** : **HTML5, CSS3, et JavaScript (Vanilla JS)**.
    *   **Rôle** : Créer l'interface utilisateur du "Mode Cérémonie", gérer les interactions (clic sur le bouton de tirage), et afficher les animations.
    *   **Librairies** : `tsParticles` pour l'animation de particules lors de la mise en relation. La communication avec le backend se fera via des requêtes `fetch` (AJAX).

*   **Base de Données** : **SQLite**.
    *   **Rôle** : Stocker de manière persistante les listes d'étudiants, les promotions et les binômes créés.
    *   **Avantage** : Fichier unique, pas de serveur de base de données à installer, ce qui simplifie le déploiement et la sauvegarde.

## 3. Structure des Fichiers du Projet

Voici l'arborescence de fichiers proposée pour organiser le projet :

```
/ParrainageApp/
|-- backend/
|   |-- app.py                # Fichier principal de l'application Flask (serveur)
|   |-- models.py             # Définition des tables de la base de données (Etudiant, Binome, etc.)
|   |-- database.py           # Logique d'initialisation et de gestion de la BDD
|   |-- routes.py             # Définition des routes de l'API (ex: /api/draw, /api/reset)
|   |-- requirements.txt      # Dépendances Python (Flask, Pandas, etc.)
|   `-- data/
|       |-- parrainage.db     # Fichier de la base de données SQLite
|       `-- students.csv      # Fichier d'exemple pour l'import
|
|-- frontend/
|   |-- index.html            # Page principale du Mode Cérémonie
|   |-- css/
|   |   `-- style.css         # Styles de la page (couleurs Keyce, mise en page)
|   `-- js/
|       |-- main.js           # Logique principale du frontend (appels API, animations)
|       `-- tsparticles.min.js # Librairie pour les animations
|
|-- specs.md                  # Le cahier des charges (existant)
|-- doc.md                    # Ce document
`-- README.md                 # Instructions pour lancer et utiliser le projet
```

## 4. Étapes de Développement

Le développement sera découpé en plusieurs étapes séquentielles :

1.  **Initialisation du Projet** :
    *   Créer la structure de dossiers et de fichiers décrite ci-dessus.
    *   Mettre en place l'environnement virtuel Python et installer les dépendances de `requirements.txt`.

2.  **Développement du Backend (Flask)** :
    *   Définir les modèles de données (`Etudiant`, `Promotion`, `Binome`) dans `models.py`.
    *   Créer le script d'initialisation de la base de données (`database.py`).
    *   Développer les routes API dans `routes.py` pour :
        *   `POST /api/import` : Importer et nettoyer un fichier CSV d'étudiants.
        *   `GET /api/draw` : Exécuter l'algorithme pour tirer un nouveau binôme.
        *   `POST /api/reset` : Réinitialiser toutes les données.
        *   `POST /api/undo` : Annuler le dernier tirage.
        *   `GET /api/export/csv` : Exporter les résultats en CSV.
        *   `GET /api/stats` : Obtenir les compteurs d'étudiants restants.
    *   Implémenter l'algorithme de parrainage dans `app.py` ou un module dédié, en respectant les règles de priorité et de gestion des pénuries.

3.  **Développement du Frontend (HTML/JS/CSS)** :
    *   Créer la structure de base de `index.html` avec les zones pour le parrain, le filleul, et les compteurs.
    *   Styliser la page `style.css` en respectant la charte graphique de Keyce (bleu nuit, orange) et en assurant un affichage plein écran.
    *   Dans `main.js`, développer la logique pour :
        *   Au chargement, récupérer les statistiques initiales (`/api/stats`).
        *   Au clic sur le bouton "Lancer le tirage", appeler l'API `/api/draw`.
        *   À la réception des données du binôme, afficher les noms et déclencher l'animation de particules avec `tsParticles`.
        *   Mettre à jour les compteurs en temps réel.

4.  **Intégration et Test** :
    *   Lancer le serveur backend et l'interface frontend simultanément.
    *   Tester le cycle complet : import -> tirages successifs -> gestion de pénurie -> reset -> export.
    *   Ajuster les animations et le style pour une expérience utilisateur fluide et agréable.
