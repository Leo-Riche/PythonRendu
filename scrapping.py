from bs4 import BeautifulSoup
import requests
import re
import csv
import os
import shutil
import matplotlib.pyplot as plt

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

def get_books_data():
    """
    On va créer deux dictionnaires :
    - Un pour le nombre de livres par catégorie
    - Un pour le prix moyen des livres par catégorie
    """
    number_books_by_category = {}
    total_price_by_category = {}
    
    for file in os.listdir('csv'):
        if file.endswith('.csv'):
            category = file.replace('.csv', '')
            total_price = 0
            number_books = 0
            
            with open(f'csv/{file}', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Extraire les prix en enlevant les symboles de monnaie et en convertissant en float
                        price = float(row['Price (incl. tax)'].replace('£', ''))
                        total_price += price
                        number_books += 1
                    except ValueError:
                       
                        continue
            
            if number_books > 0:
                number_books_by_category[category] = number_books
                total_price_by_category[category] = total_price / number_books  

    return number_books_by_category, total_price_by_category

def plot_books_pie_chart(data):
    """
    Crée un diagramme en camembert représentant la proportion de livres par catégorie
    """
    categories = list(data.keys())
    number_books = list(data.values())

    plt.figure(figsize=(10, 10))
    plt.pie(number_books, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title('Pourcentage de livres par catégorie')
    plt.show()

def plot_average_price_bar_chart(data):
    """
    Crée un graphique en barres représentant le prix moyen des livres par catégorie
    """
    categories = list(data.keys())
    average_prices = list(data.values())

    plt.figure(figsize=(10, 6))
    plt.bar(categories, average_prices, color='skyblue')
    plt.xlabel('Catégories')
    plt.ylabel('Prix moyen (£)')
    plt.title('Prix moyen des livres par catégorie')
    plt.xticks(rotation=45, ha='right') 
    plt.tight_layout()  
    plt.show()

number_books_by_category, average_price_by_category = get_books_data()

plot_books_pie_chart(number_books_by_category)

plot_average_price_bar_chart(average_price_by_category)