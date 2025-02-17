import requests
from bs4 import BeautifulSoup
import csv
import os
import datetime

# Création du dossier de base avec la date et l'heure de l'extraction afin de pouvoir comparer les prix aux différentes dates
BASE_FOLDER = "Extraction_bookstoscrap_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
os.makedirs(BASE_FOLDER, exist_ok=True)

url_de_base = 'https://books.toscrape.com/index.html'

# Extraire toutes les catégories sur le site depuis l'URL de base
def extract_all_categories(url_de_base):
    response = requests.get(url_de_base)
    soup = BeautifulSoup(response.text, 'html.parser')
    categories_urls = {}
    navigation_list = soup.find('ul', class_='nav nav-list')
    balises_a = navigation_list.find_all('a')
    for categorie_url in balises_a[1:]:
        une_categorie = "https://books.toscrape.com/" + categorie_url['href']
        category_name = categorie_url.text.strip()
        categories_urls[category_name] = une_categorie
    return categories_urls


# Récupérer toutes les URLs des livres d'une catégorie
def extract_books_urls_from_une_categorie(category_url):
    url_de_tous_les_livres = []
    current_page_url = category_url
    # Récupérer la première page pour extraire le nombre total de livres annoncé afin de pouvoir le comparer au total de livres extraits
    response = requests.get(current_page_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    form = soup.find('form', method='get', class_='form-horizontal')
    nb_livres = form.find('strong')
    total_books_announced = int(nb_livres.text.strip())

    # Parcourir les pages de la catégorie
    while True:
        response = requests.get(current_page_url)
        soup = BeautifulSoup(response.text, 'html.parser')
    
        toutes_les_balises_h3 = soup.find_all('h3')
        for chaque_balise_h3 in toutes_les_balises_h3:
            url_dun_livre = 'https://books.toscrape.com/catalogue' + chaque_balise_h3.find('a')['href'][8:]
            url_de_tous_les_livres.append(url_dun_livre)
        
        next_button = soup.find('li', class_='next')
        if next_button:
            next_page = next_button.find('a')['href']
            current_page_url = current_page_url.replace('index.html', next_page)
        else:
            break

    return url_de_tous_les_livres


# Fonction pour extraire les informations d'un livre
def extract_book_info(book_url, category_name):
    response = requests.get(book_url)
    response.encoding = 'utf-8'  # Forcer l'encodage à cause des caractères spéciaux 
    soup = BeautifulSoup(response.text, 'html.parser')
    page_url = book_url
    category = soup.find('ul', class_='breadcrumb').find_all('li')[2].text.strip()
    star_rating_class = soup.find('p', class_='star-rating')['class'][1]  
    image_url = soup.find('img')['src']
    image_url = 'https://books.toscrape.com/' + image_url[6:] 
    table = soup.find('table', class_='table table-striped')
    upc = table.find('td').text.strip()
    title = soup.find('h1').text.strip()
    price_excl_tax = table.find_all('td')[2].text.strip().replace("Â£", "£")
    price_incl_tax = table.find_all('td')[3].text.strip().replace("Â£", "£")
    availability = table.find_all('td')[5].text.strip()
    product_description_div = soup.find('div', id='product_description')
    product_description = (product_description_div.find_next('p').text.strip()) if product_description_div else 'N/A' #car j'ai eu un livre sans description

    # Téléchargement de l'image
    save_image(image_url, title, category_name)
    return [page_url, upc, title, price_incl_tax, price_excl_tax, availability, 
            product_description, category, star_rating_class, image_url]

# On appelle la fonction pour créer les URLs des catégories
categorie_urls = extract_all_categories(url_de_base)

# Vérifier que le nombre de catégories extraites est bien de 50
if len(categorie_urls) != 50:
    print(f"Attention : {len(categorie_urls)} catégories extraites, mais 50 sont attendues.")
else:
    print("OK : 50 catégories extraites.")

# Générer un fichier CSV pour chaque catégorie
def create_csv_for_category(category_name, category_url):
    books_urls = extract_books_urls_from_une_categorie(category_url)
    
    # Créer un dossier pour la catégorie
    category_folder = os.path.join(BASE_FOLDER, category_name)
    os.makedirs(category_folder, exist_ok=True)
    csv_path = os.path.join(category_folder, f'{category_name}_book_infos.csv')
    with open(csv_path, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(['product_page_url', 'universal_product_code', 'title', 
                         'price_including_tax', 'price_excluding_tax', 'number_available', 
                         'product_description', 'category', 'review_rating', 'image_url'])
        
        for book_url in books_urls:
            book_info = extract_book_info(book_url, category_name)
            if len(book_info) != 10:
                print(f"Attention : le livre {book_url} ne contient que {len(book_info)} informations.")
            else:
                writer.writerow(book_info)

       # Vérification si le nombre de livres extraits et d'images téléchargées est le même
    images_folder = os.path.join(category_folder, 'images')
    downloaded_images = len([f for f in os.listdir(images_folder)])
    if downloaded_images != len(books_urls):
        print(f"Attention dans {category_name} : {len(books_urls)} livres extraits, mais {downloaded_images} images téléchargées.")
    else:
        print(f"OK pour {category_name} : {len(books_urls)} livres extraits et {downloaded_images} images téléchargées.")


# Sauvegarde des images téléchargées
def save_image(image_url, title, category_name):
    response = requests.get(image_url) 
    category_images_folder = os.path.join(BASE_FOLDER, category_name, "images")
    os.makedirs(category_images_folder, exist_ok=True)  #Créer le dossier s'il n'existe pas et permet d'éviter une erreur si le dossier existe
    
    #pour chaque caractère dans le titre, si c'est n'est pas alphanumérique, il le transforme en _ pour éviter les problème d'enregistrement.
    #ensuite il va concaténer tous les caractères, sans espace ("")
    image_title = "".join([char if char.isalnum() else "_" for char in title])[:100]
    existing_images = [f for f in os.listdir(category_images_folder)]
    next_number = len(existing_images) + 1
    #la fonction os.path permet de crée un chemin de fichier selon notre système d'exploitation
    image_name = os.path.join(category_images_folder, f"{next_number}_{image_title}.jpg")
    
    with open(image_name, 'wb') as file:
        file.write(response.content)        


# EXECUTION DU CODE : Création des CSV pour chaque catégorie
for category_name, category_url in categorie_urls.items():
    create_csv_for_category(category_name, category_url)
