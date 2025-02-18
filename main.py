import requests
from bs4 import BeautifulSoup
import csv
import os
import datetime
from urllib.parse import urljoin

# Création du dossier de base avec la date et l'heure de l'extraction afin 
# de pouvoir comparer les prix aux différentes dates
BASE_FOLDER = "Extract_bookstoscrap_" + datetime.datetime.now().strftime("%Y%m%d_%H%M")
os.makedirs(BASE_FOLDER, exist_ok=True)

base_url = 'https://books.toscrape.com/index.html'

# Extraction de toutes les catégories sur le site depuis l'URL de base
def extract_all_categories(base_url):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    categories_urls = {}
    navigation_list = soup.find('ul', class_='nav nav-list')
    a_tag = navigation_list.find_all('a')
    for categorie_url in a_tag[1:]:
        categorie_urls = "https://books.toscrape.com/" + categorie_url['href']
        category_name = categorie_url.text.strip()
        categories_urls[category_name] = categorie_urls
    return categories_urls


# Récupérer toutes les URLs des livres d'une catégorie
def extract_books_urls_from_all_categories(category_url):
    books_urls = []
    current_page_url = category_url
    # Récupérer la première page pour extraire le nombre total de 
    # livres annoncé afin de pouvoir le comparer au total de livres extraits
    response = requests.get(current_page_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    form = soup.find('form', method='get', class_='form-horizontal')
    books_number = form.find('strong')
    total_books_announced = int(books_number.text.strip())

    # Parcourir les pages de la catégorie
    while True:
        response = requests.get(current_page_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        h3_tag = soup.find_all('h3')
        for book_urls in h3_tag:
            book_url = 'https://books.toscrape.com/catalogue' + book_urls.find('a')['href'][8:]
            books_urls.append(book_url)
        
        next_button = soup.find('li', class_='next')
        if next_button:
            next_page = next_button.find('a')['href']
            current_page_url = urljoin(current_page_url, next_page)
        else:
            break

    return books_urls


# Fonction pour extraire les informations d'un livre
def extract_book_info(book_url, category_name):
    response = requests.get(book_url)
    response.encoding = 'utf-8' 
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
    if product_description_div:
        product_description = (product_description_div.find_next('p').text.strip())  
    else:
        product_description = 'N/A'

    # Sauvegarde des images téléchargées
    response = requests.get(image_url) 
    category_images_folder = os.path.join(BASE_FOLDER, category_name, "images")
    os.makedirs(category_images_folder, exist_ok=True) 
    image_title = "".join([c if c.isalnum() else "_" for c in title])[:70]
    image_name = os.path.join(category_images_folder, f"{image_title}_{upc}.jpg")
    
    with open(image_name, 'wb') as file:
        file.write(response.content)        
    return [page_url, upc, title, price_incl_tax, price_excl_tax, availability, 
            product_description, category, star_rating_class, image_url]


# Générer un fichier CSV pour chaque catégorie
def create_csv_for_category(category_name, category_url):
    books_urls = extract_books_urls_from_all_categories(category_url)
    
    # Créer un dossier pour la catégorie
    category_folder = os.path.join(BASE_FOLDER, category_name)
    os.makedirs(category_folder, exist_ok=True)
    csv_path = os.path.join(category_folder, f'{category_name}_book_infos.csv')
    with open(csv_path, mode='w', newline='', encoding='utf-8-sig') as file:
        row_count = 0
        writer = csv.writer(file)
        writer.writerow(['product_page_url', 'universal_product_code', 
                        'title', 'price_including_tax', 'price_excluding_tax',
                        'number_available', 'product_description', 'category',
                        'review_rating', 'image_url'])
        
        for book_url in books_urls:
            book_info = extract_book_info(book_url, category_name)
            if len(book_info) != 10:
                print(f"Attention : le livre {book_url} ne contient" 
                      f"que {len(book_info)} informations.")
            else:
                writer.writerow(book_info)
                row_count += 1

       # Vérification si le nombre de lignes dans le CSV, le nombre de livre sur le 
       # site d'images téléchargées est le même
    images_folder = os.path.join(category_folder, 'images')
    downloaded_images = len([f for f in os.listdir(images_folder)])
    num_books = len(books_urls)
    if num_books == row_count == downloaded_images:
        print(f"OK pour {category_name} : {num_books} URLs de livres,"
              f"{row_count} lignes dans le CSV,"
              f"et {downloaded_images} images téléchargées.")
    else:
        print(f"Attention dans {category_name} : {num_books} URLs de livres,"
             f" {row_count} lignes dans le CSV,"
             f" mais {downloaded_images} images téléchargées.")


# On appelle la fonction pour créer les URLs des catégories
categorie_urls = extract_all_categories(base_url)
# Vérifier que le nombre de catégories extraites est bien de 50
if len(categorie_urls) != 50:
    print(f"Attention : {len(categorie_urls)} catégories extraites,"
          f"mais 50 sont attendues.")
else:
    print("OK : 50 catégories extraites.")

# EXECUTION DU CODE : Création des CSV pour chaque catégorie
for category_name, category_url in categorie_urls.items():
    create_csv_for_category(category_name, category_url)
