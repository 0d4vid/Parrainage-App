# CAHIER DES CHARGES : Logiciel de Gestion du Parrainage - Keyce Informatique

Voici une rédaction structurée et technique du projet de "Logiciel de Gestion du Parrainage" pour Keyce Informatique, basée sur les documents fournis.

-----

# Projet : Application de Gestion du Parrainage - Keyce Informatique

## 1\. Spécifications Fonctionnelles et Non Fonctionnelles

Cette section détaille ce que le logiciel doit faire (fonctionnel) et comment il doit se comporter (non fonctionnel), conformément à la demande du Bureau des Étudiants (BDE).

### A. Spécifications Fonctionnelles

Ces fonctionnalités couvrent le cycle de vie de l'application, de l'importation des données à l'exportation des résultats.

  * **Gestion des Données (Back-office / Admin)**

      * [cite_start]**Importation :** Le système doit permettre l'import manuel ou via fichier CSV des listes d'étudiants[cite: 71].
      * [cite_start]**Nettoyage :** Capacité à supprimer les doublons et nettoyer les données importées[cite: 72].
      * [cite_start]**Stockage :** Enregistrement du nom, prénom, matricule (facultatif), promotion et statut (parrainé/parrain/disponible)[cite: 30, 31, 32, 33].
      * [cite_start]**Exportation :** Génération des résultats finaux sous format PDF ou CSV[cite: 73].

  * **Cœur du Système : Algorithme de Parrainage**

      * [cite_start]**Tirage Automatique :** Attribution aléatoire des binômes selon les règles de promotion définies[cite: 34].
      * [cite_start]**Gestion des déséquilibres :** Si le nombre de filleuls dépasse le nombre de parrains, l'algorithme doit attribuer plusieurs filleuls à un même parrain[cite: 58, 59].
      * [cite_start]**Équilibrage :** Priorité donnée aux parrains n'ayant pas encore de filleul avant d'en attribuer un second[cite: 54, 55].
      * [cite_start]**Réinitialisation :** Présence d'un bouton "RESET" pour recommencer le tirage à zéro[cite: 61].
      * [cite_start]**Annulation :** Possibilité d'annuler la dernière attribution effectuée[cite: 81].

  * **Interface Utilisateur & Animation (Mode Cérémonie)**

      * [cite_start]**Affichage :** Présentation côte-à-côte du parrain et du filleul[cite: 65].
      * [cite_start]**Animation :** Visualisation obligatoire de la mise en relation (particules, ligne, lumière) avec une transition élégante[cite: 39, 43, 44].
      * [cite_start]**Indicateurs :** Affichage d'un compteur de parrains et filleuls restants[cite: 68].

### B. Spécifications Non Fonctionnelles

  * [cite_start]**Délai critique :** Le logiciel doit être fonctionnel pour le **lundi suivant la demande** (tests internes) et prêt pour la cérémonie du vendredi[cite: 12, 83].
  * [cite_start]**Expérience Utilisateur (UX/UI) :** Design propre respectant les couleurs de Keyce (bleu nuit et orange), intuitif et adapté à une projection sur vidéoprojecteur (plein écran)[cite: 64, 75, 77, 89].
  * [cite_start]**Fiabilité et Sécurité :** Sauvegarde automatique des résultats et garantie qu'aucun filleul n'est sélectionné deux fois[cite: 48, 79, 80].

-----

## 2\. Règles de Logique (Règles Métier)

L'algorithme doit respecter strictement la hiérarchie académique et les contraintes d'unicité définies par le BDE.

### A. Hiérarchie de Parrainage

[cite_start]Les binômes sont formés selon les correspondances de promotions suivantes[cite: 34]:

  * [cite_start]**B2** parraine **B1**[cite: 35].
  * [cite_start]**B3** parraine **B2**[cite: 36].
  * [cite_start]**M1** parraine **B3**[cite: 37].
  * [cite_start]**M2** parraine **M1**[cite: 38].

### B. Contraintes de Cardinalité

1.  **Unicité du Filleul :** Un étudiant ne peut avoir qu'un seul parrain. [cite_start]Une fois choisi comme filleul, il est retiré immédiatement de la liste des disponibles[cite: 47, 51, 52].
2.  [cite_start]**Multiplicité du Parrain :** Un parrain peut avoir plusieurs filleuls **uniquement** si le nombre de filleuls est supérieur au nombre de parrains disponibles (pénurie de parrains)[cite: 49, 50].

### C. Gestion des États

  * [cite_start]Si **Filleul** est sélectionné $\rightarrow$ Statut devient "Parrainé" (retiré de la liste de tirage)[cite: 52].
  * [cite_start]Si **Parrain** est sélectionné $\rightarrow$ Statut reste "Disponible" mais sa priorité baisse (mis en fin de file d'attente pour l'équilibrage)[cite: 53, 54].

-----

## 3\. Modèle Conceptuel de Données (MCD)

Pour modéliser ce système, nous identifions les entités principales. Notez que la distinction "Parrain" et "Filleul" est relative (un B2 est parrain d'un B1 mais filleul d'un B3), donc nous utiliserons une entité unique `ETUDIANT` avec une auto-association.

**Entités et Propriétés :**

  * **PROMOTION**

      * `Code_Promo` (Identifiant: B1, B2, etc.)
      * `Libellé`

  * **ETUDIANT**

      * `ID_Etudiant` (Identifiant unique)
      * [cite_start]`Nom` [cite: 32]
      * [cite_start]`Prénom` [cite: 32]
      * [cite_start]`Matricule` [cite: 32]
      * [cite_start]`Statut` (Disponible, Parrainé, Parrain) [cite: 33]

**Association :**

  * **PARRAINER** (Relation réflexive sur Étudiant)
      * Un étudiant (Parrain) parraine un autre étudiant (Filleul).

-----

## 4\. Relations entre les entités (Cardinalités)

Les relations se définissent comme suit dans le modèle conceptuel :

1.  **ETUDIANT - APPARTENIR - PROMOTION**

      * Un étudiant appartient à **1 et 1 seule** promotion.
      * Une promotion contient **1 à N** étudiants.
      * *(0,1) coté Etudiant / (1,n) coté Promotion*.

2.  **ETUDIANT (Parrain) - PARRAINER - ETUDIANT (Filleul)**

      * [cite_start]**Coté Parrain :** Un étudiant peut parrainer **0 à N** étudiants (0 au début, N en cas de pénurie de parrains)[cite: 49].
      * [cite_start]**Coté Filleul :** Un étudiant peut être parrainé par **0 à 1** étudiant (0 au début, 1 maximum à la fin)[cite: 47].

-----

## 5\. Modèle Logique de Données (MLD)

Traduction du modèle conceptuel en structure de tables relationnelles (type SQL). Les clés primaires sont soulignées et les clés étrangères précédées d'un `#`.

  * **TABLE PROMOTION**

      * \<u\>id\_promo\</u\> (INT)
      * code\_promo (VARCHAR) : *Ex: 'B1', 'M2'*

  * **TABLE ETUDIANT**

      * \<u\>id\_etudiant\</u\> (INT)
      * [cite_start]matricule (VARCHAR) [cite: 32]
      * [cite_start]nom (VARCHAR) [cite: 32]
      * [cite_start]prenom (VARCHAR) [cite: 32]
      * [cite_start]statut (ENUM) : *'disponible', 'parrain', 'parrainé'* [cite: 33]
      * [cite_start]\#id\_promo (INT) : *Clé étrangère vers PROMOTION* [cite: 31]

  * **TABLE BINOME** (Matérialisation de l'association "Parrainer")

      * Cette table enregistre les paires générées.
      * \<u\>id\_binome\</u\> (INT)
      * [cite_start]\#id\_filleul (INT) : *Clé étrangère vers ETUDIANT (Doit être UNIQUE pour respecter la règle "Un étudiant NE PEUT PAS avoir 2 parrains" [cite: 47])*
      * \#id\_parrain (INT) : *Clé étrangère vers ETUDIANT*
      * [cite_start]date\_creation (DATETIME) : *Utile pour l'historique ou l'annulation [cite: 81]*

*Note technique pour le développement : L'algorithme devra faire une jointure entre `ETUDIANT` (Filleul potentiel) et `ETUDIANT` (Parrain potentiel) en vérifiant que `id_promo_parrain` correspond à la règle de gestion vis-à-vis de `id_promo_filleul` (ex: Si Filleul est B1, Parrain doit être B2).*

## 1. Architecture Technique (Stack Technologique)

Ce projet repose sur une architecture client-serveur locale, garantissant à la fois la robustesse des données et la fluidité visuelle requise pour la cérémonie.

* **Backend (Cœur Logique) : Python avec Flask (ou FastAPI)**
    * [cite_start]**Rôle :** Il gère toute la logique métier complexe (algorithme de tirage, règles d'équilibrage, gestion des doublons)[cite: 34, 46]. Il expose des "routes" (API) que l'interface appelle.
    * [cite_start]**Avantage :** Python est idéal pour manipuler les listes d'étudiants et garantir qu'aucun bug logique ne survienne lors de l'attribution[cite: 87].
    * **Librairies clés :** `Pandas` (pour l'import/export CSV efficace), `SQLAlchemy` (pour gérer la base de données).

* **Frontend (Interface Visuelle) : HTML5 / CSS3 / JavaScript**
    * **Rôle :** Assurer l'affichage "Cérémonie" en plein écran avec les animations demandées (particules, transitions).
    * [cite_start]**Technologie :** Utilisation d'un framework léger comme **Vue.js** (via CDN pour simplifier) ou Vanilla JS, couplé à une librairie d'animation (ex: `tsParticles` ou `Anime.js`) pour l'effet visuel de connexion[cite: 43].
    * **Communication :** Le Frontend envoie des requêtes AJAX (`fetch`) au Backend pour demander "Génère un nouveau couple" et affiche le résultat JSON reçu.

* **Base de Données : SQLite**
    * **Rôle :** Stockage persistant des données dans un fichier unique (ex: `parrainage.db`).
    * [cite_start]**Avantage :** Pas d'installation de serveur lourd requise, sauvegarde facile (copier-coller du fichier), et fiabilité SQL pour les requêtes complexes[cite: 80].

---

## 2. Spécifications Fonctionnelles et Non Fonctionnelles

### A. Fonctionnalités (Back-End & Front-End)
1.  **Administration et Données**
    * [cite_start]Importation des listes d'étudiants (CSV) et nettoyage des données (suppression doublons)[cite: 71, 72].
    * [cite_start]Exportation de la liste finale des binômes en PDF et CSV[cite: 73].
    * [cite_start]Fonction "Reset" pour remettre à zéro la base de données[cite: 61].
    * [cite_start]Fonction "Annuler" pour supprimer la dernière paire générée en cas d'erreur[cite: 81].

2.  **Cœur du Parrainage (Algorithme Python)**
    * Attribution d'un parrain à un filleul selon les règles de promotion définies.
    * [cite_start]Gestion automatique de la pénurie : si plus de filleuls que de parrains, un parrain peut se voir attribuer un second filleul[cite: 49, 58].

3.  **Mode Cérémonie (Interface)**
    * [cite_start]Affichage plein écran compatible vidéoprojecteur[cite: 75].
    * Bouton unique "Lancer le tirage" pour générer une paire en direct.
    * [cite_start]**Animation obligatoire :** Transition visuelle (particules, lumière) reliant les noms du parrain et du filleul[cite: 39, 43].
    * [cite_start]Affichage en temps réel du compteur de "Restants"[cite: 68].

### B. Contraintes Non Fonctionnelles
* [cite_start]**Fiabilité :** Le système doit garantir l'intégrité des données (ACID via SQLite) ; un filleul ne doit jamais ressortir deux fois[cite: 48, 79].
* **Performance :** L'animation doit être fluide, sans latence perceptible lors du tirage.
* [cite_start]**Esthétique :** Respect de la charte graphique Keyce[cite: 64].

---

## 3. Règles de Logique (Algorithme Métier)

Ces règles seront implémentées directement dans le code Python (Backend).

[cite_start]**Règles de Correspondance (Hard-coded) [cite: 34-38] :**
* **Groupe 1 :** Les **B2** parrainent les **B1**.
* **Groupe 2 :** Les **B3** parrainent les **B2**.
* **Groupe 3 :** Les **M1** parrainent les **B3**.
* **Groupe 4 :** Les **M2** parrainent les **M1**.

**Algorithme d'Attribution Dynamique :**
1.  **Vérification :** L'algorithme vérifie s'il reste des filleuls dans la promo cible.
2.  **Sélection Parrain :**
    * *Priorité 1 :* Parrains de la promo supérieure ayant **0 filleul**.
    * [cite_start]*Priorité 2 (si liste 1 vide) :* Parrains ayant déjà **1 filleul** (uniquement en cas de déséquilibre)[cite: 54, 59].
3.  **Marquage :**
    * [cite_start]Le filleul passe au statut `PARRAINÉ` (ne peut plus être tiré)[cite: 52].
    * Le parrain voit son compteur de filleuls incrémenté.

---

## 4. Modèle Conceptuel de Données (MCD)

Nous utilisons une structure centrée sur l'individu, car un étudiant change de rôle (parrain/filleul) selon sa promotion.

**Entités :**

* **PROMOTION**
    * `Code_Promo` (Id : B1, B2, B3, M1, M2)
    * `Libellé`

* **ETUDIANT**
    * `Matricule` (Identifiant unique)
    * `Nom`
    * `Prénom`
    * `Statut_Actuel` (Disponible, Parrainé)
    * `Nb_Filleuls_Attribues` (Entier, par défaut 0)

**Association :**

* **EST_PARRAINÉ_PAR** (Relation réflexive)
    * Relie un étudiant (Filleul) à un autre étudiant (Parrain).
    * Propriété de l'association : `Date_Parrainage`.

---

## 5. Relations entre les Entités (Cardinalités)

* **ETUDIANT** --(1,1)-- **APPARTENIR** --(1,n)-- **PROMOTION**
    * *Tout étudiant est dans une seule promotion.*

* **ETUDIANT (Filleul)** --(0,1)-- **AVOIR_PARRAIN** --(0,n)-- **ETUDIANT (Parrain)**
    * [cite_start]*Un filleul a au maximum 1 parrain (0 avant le tirage).* [cite: 47]
    * [cite_start]*Un parrain peut avoir plusieurs filleuls (0 au début, N si besoin).* [cite: 49]

---

## 6. Modèle Logique de Données (MLD - Structure SQLite)

Voici la structure exacte des tables à créer dans SQLite.

1.  **Table `promotions`**
    * `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
    * `code` (TEXT UNIQUE) : 'B1', 'B2'...

2.  **Table `etudiants`**
    * `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
    * `matricule` (TEXT UNIQUE)
    * `nom` (TEXT)
    * `prenom` (TEXT)
    * `promo_code` (TEXT) : Clé étrangère logique vers `promotions(code)`
    * `nb_filleuls` (INTEGER DEFAULT 0) : *Permet de gérer la priorité des parrains.*
    * `est_parraine` (BOOLEAN DEFAULT 0) : *Si 1, exclu des futurs tirages en tant que filleul.*

3.  **Table `binomes`** (Table de liaison pour l'historique)
    * `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
    * `filleul_id` (INTEGER UNIQUE) : *Clé étrangère vers etudiants. UNIQUE garantit qu'un étudiant n'est filleul qu'une fois.*
    * `parrain_id` (INTEGER) : *Clé étrangère vers etudiants.*
    * `timestamp` (DATETIME DEFAULT CURRENT_TIMESTAMP)