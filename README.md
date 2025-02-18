# Projet2_Elodie_Fourcade
Création d'un système de surveillance des prix du site https://books.toscrape.com/index.html

Utilisation de Python 3.13.1

```bash
Etapes à suivres :
- cloner le repository github en local
- créer l'environnement virtuel : 
py -m venv .venv
- activer l'environnement virtuel : 
.venv\Scripts\activate
- installer les dépendances : 
pip install -r requirements.txt
- exécuter le script :
py main.py

Voici la structure attendu lors de l'exécution du script main.py :
└── Extract_bookstoscrap_YYYYMMDD_HHMM 
    ├── [Nom de la catégorie]
    │   ├── [NomDeLaCategorie_book_infos.csv]  
    │   └── images                
    └── ...