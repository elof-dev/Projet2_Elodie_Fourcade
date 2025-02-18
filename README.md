# Création d'un système de surveillance des prix du site https://books.toscrape.com/index.html

## Pré-requis

Utilisation de Python 3.13.1

## Etapes à suivres :
- cloner le repository github en local
- créer l'environnement virtuel : 
```bash py -m venv .venv```
- activer l'environnement virtuel : 
```bash .venv\Scripts\activate```
- installer les dépendances : 
```bash pip install -r requirements.txt```
- exécuter le script :
```bash py main.py```

Voici la structure attendu lors de l'exécution du script main.py :
└── Extract_bookstoscrap_YYYYMMDD_HHMM 
    ├── [Nom de la catégorie]
    │   ├── [NomDeLaCategorie_book_infos.csv] 
    │   └── images                
    └── ...