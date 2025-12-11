# Mord ton Pion - Projet BDW

## Structure du projet

```
morpion/
├── controleurs/          # Contrôleurs Python
│   ├── accueil.py
│   ├── creer_equipe.py
│   ├── equipes.py
│   ├── historique.py
│   ├── includes.py
│   ├── partie_avancee.py
│   └── partie_normale.py
├── model/                # Modèle (accès BD)
│   └── model_pg.py
├── static/               # Fichiers statiques
│   ├── css/
│   │   └── style.css
│   └── img/              # ⚠️ METTRE LES IMAGES ICI
│       ├── t1.png à t10.png (morpions)
│       ├── sheep.png (logo)
│       └── by-nc-sa-eu.png (licence)
├── templates/            # Templates HTML/Jinja
│   ├── accueil.html
│   ├── base.html
│   ├── creer_equipe.html
│   ├── equipes.html
│   ├── footer.html
│   ├── header.html
│   ├── historique.html
│   ├── menu.html
│   ├── message.html
│   ├── partie_avancee.html
│   └── partie_normale.html
├── historiques/          # Fichiers historiques générés
├── code_sql.sql          # Script SQL pour créer la BD
├── init.py               # Initialisation
├── routes.toml           # Configuration des routes
└── README.md             # Ce fichier
```

## Installation

1. Copier le dossier `morpion` dans le dossier `websites` de bdw-server

2. Exécuter le script SQL `code_sql.sql` dans PostgreSQL pour créer les tables

3. Ajouter les images dans `static/img/` :
   - t1.png à t10.png (images des morpions)
   - sheep.png (logo du site)
   - by-nc-sa-eu.png (logo licence Creative Commons)

4. Lancer le serveur bdw-server

## Fonctionnalités

- ✅ Page d'accueil avec statistiques
- ✅ Création d'équipes (6-8 morpions)
- ✅ Liste et suppression d'équipes
- ✅ Partie normale (morpion classique)
- 🔜 Partie avancée (avec combats et sorts)
- ✅ Historique des activités

## Auteur

Projet réalisé dans le cadre de l'UE BDW - Lyon 1
