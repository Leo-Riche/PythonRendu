from bs4 import BeautifulSoup
import requests
import re
import csv
import os
import shutil

url = "https://books.toscrape.com/"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

if not os.path.exists('images'):
    if not os.path.exists('images'):
        os.makedirs('images')
    else:
        for filename in os.listdir('images'):
            file_path = os.path.join('images', filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

if not os.path.exists('csv'):
    os.makedirs('csv') 

def getBook(soup, url):
    """
    Extrait les informations d'un livre à partir de la page de détails du livre.

    Args:
        soup (BeautifulSoup): L'objet BeautifulSoup contenant le contenu HTML de la page du livre.
        url (str): L'URL de la page du livre.

    Returns:
        tuple: Un tuple contenant les informations du livre (URL, UPC, titre, prix TTC, prix HT, disponibilité, description, catégorie, note de critique, URL de l'image).
    """
    book_infos = soup.select("td")
    book_url = url
    book_upc = book_infos[0].text
    book_title = soup.select("h1")[0].text
    book_price_including_taxe = book_infos[3].text.replace('Â', '')
    book_price_excluding_taxe = book_infos[2].text.replace('Â', '')
    book_number_available = book_infos[5].text
    book_number_available = re.search(r'\d+', book_number_available).group()
    book_description = soup.select("article > p")[0].text
    book_category = soup.select("ul > li")[2].text.strip()
    book_review_rating = soup.find_all("p", class_="star-rating")[0]['class'][1]
    book_img_url = "books.toscrape.com" + soup.select("img")[0]["src"].replace('../..', '')

    return (book_url, book_upc, book_title, book_price_including_taxe, book_price_excluding_taxe, book_number_available, book_description, book_category, book_review_rating, book_img_url)

def getAllBooksOfCategory(soup, url, category_number):
    """
    Extrait les informations de tous les livres d'une catégorie spécifique et les enregistre dans un fichier CSV.

    Args:
        soup (BeautifulSoup): L'objet BeautifulSoup contenant le contenu HTML de la page principale.
        url (str): L'URL de la page principale.
        category_number (int): Le numéro de la catégorie à extraire.

    Returns:
        None
    """
    try:
        category_url = url + soup.select("ul > li > a")[category_number]["href"]
        response = requests.get(category_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        book_data = []

        while True:
            books = soup.select("article > div > a")

            for book in books:
                book_url = url + 'catalogue/' + book['href'].replace('../../../', '')
                response = requests.get(book_url)
                book_soup = BeautifulSoup(response.content, 'html.parser')
                book_data.append(getBook(book_soup, book_url))

            next_button = soup.find('li', class_='next')
            if next_button:
                next_button_url = next_button.find('a')['href']
                response = requests.get(category_url.rsplit('/', 1)[0] + '/' + next_button_url)
                soup = BeautifulSoup(response.content, 'html.parser')
            else:
                break

        for book in book_data:
            book_img_url = book[9]
            img_response = requests.get('http://' + book_img_url)
            if img_response.status_code == 200:
                img_name = re.sub(r'[^\w\s-]', '', book[2]) + '.jpg'
                img_name = img_name.replace(' ', '_')
                with open(f'images/{img_name}', 'wb') as img_file:
                    img_file.write(img_response.content)

    except Exception as e:
        print(f"La catégorie {category_number} n'existe pas ou une erreur s'est produite: {e}")

    with open('csv/book_data.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['URL', 'UPC', 'Title', 'Price (incl. tax)', 'Price (excl. tax)', 'Availability', 'Description', 'Category', 'Review Rating', 'Image URL'])
        writer.writerows(book_data)
        
def getAllBooksOfAllCategories(soup, url):
    """
    Extrait les informations de tous les livres de toutes les catégories et les enregistre dans des fichiers CSV distincts pour chaque catégorie.

    Args:
        soup (BeautifulSoup): L'objet BeautifulSoup contenant le contenu HTML de la page principale.
        url (str): L'URL de la page principale.

    Returns:
        None
    """
    try:
        categories = soup.select("ul > li > a")
        for category_number in range(2, len(categories)):
            category_name = categories[category_number].text.strip()
            category_folder = os.path.join('images', category_name)
            if not os.path.exists(category_folder):
                os.makedirs(category_folder)
            getAllBooksOfCategory(soup, url, category_number, category_folder, category_name)
    except Exception as e:
        print(f"Une erreur s'est produite: {e}")

def getAllBooksOfCategory(soup, url, category_number, category_folder, category_name):
    """
    Extrait les informations de tous les livres d'une catégorie spécifique et les enregistre dans un fichier CSV.

    Args:
        soup (BeautifulSoup): L'objet BeautifulSoup contenant le contenu HTML de la page principale.
        url (str): L'URL de la page principale.
        category_number (int): Le numéro de la catégorie à extraire.
        category_folder (str): Le dossier où enregistrer les images de la catégorie.
        category_name (str): Le nom de la catégorie pour nommer le fichier CSV.

    Returns:
        None
    """
    try:
        category_url = url + soup.select("ul > li > a")[category_number]["href"]
        response = requests.get(category_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        book_data = []

        while True:
            books = soup.select("article > div > a")

            for book in books:
                book_url = url + 'catalogue/' + book['href'].replace('../../../', '')
                response = requests.get(book_url)
                book_soup = BeautifulSoup(response.content, 'html.parser')
                book_data.append(getBook(book_soup, book_url))

            next_button = soup.find('li', class_='next')
            if next_button:
                next_button_url = next_button.find('a')['href']
                response = requests.get(category_url.rsplit('/', 1)[0] + '/' + next_button_url)
                soup = BeautifulSoup(response.content, 'html.parser')
            else:
                break 

        for book in book_data:
            book_img_url = book[9]
            img_response = requests.get('http://' + book_img_url)
            if img_response.status_code == 200:
                img_name = re.sub(r'[^\w\s-]', '', book[2]) + '.jpg'
                img_name = img_name.replace(' ', '_')
                with open(f'{category_folder}/{img_name}', 'wb') as img_file:
                    img_file.write(img_response.content)

    except Exception as e:
        print(f"La catégorie {category_number} n'existe pas ou une erreur s'est produite: {e}")

    csv_filename = f'csv/{category_name}.csv'
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['URL', 'UPC', 'Title', 'Price (incl. tax)', 'Price (excl. tax)', 'Availability', 'Description', 'Category', 'Review Rating', 'Image URL'])
        writer.writerows(book_data)

getAllBooksOfAllCategories(soup, url)