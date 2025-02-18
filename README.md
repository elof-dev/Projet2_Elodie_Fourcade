## Création d'un système de surveillance des prix du site https://books.toscrape.com/index.html

## Pré-requis

Utilisation de Python 3.13.1

## Etapes à suivres :

- cloner le repository github en local : ``https://github.com/elof-dev/Projet2_Elodie_Fourcade.git``

- se positionner sur le dossier : ``Projet2_Elodie_Fourcade``

- créer l'environnement virtuel : ``py -m venv .venv``

- activer l'environnement virtuel : `` .venv\Scripts\activate``

- installer les dépendances :  ``pip install -r requirements.txt``

- exécuter le script : ``py main.py``
```bash
Voici la structure attendu lors de l'exécution du script main.py :
└── Extract_bookstoscrap_YYYYMMDD_HHMM 
    ├── [Nom de la catégorie]
    │   ├── [NomDeLaCategorie_book_infos.csv] 
    │   └── images                
    └── ...