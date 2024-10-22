from bs4 import BeautifulSoup
import requests
import csv
import os

url = "https://books.toscrape.com/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

book = soup.select("article > div > a")

url += book[0]['href']
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

book_infos = soup.select("td")
book_url = url
book_upc = book_infos[0].text
book_product_type = book_infos[1].text
book_title = soup.select("h1")[0].text
book_price_including_taxe = book_infos[3].text.replace('Â', '')
book_price_excluding_taxe = book_infos[2].text.replace('Â', '')
book_number_available = book_infos[5].text
book_description = soup.select("article > p")[0].text
book_category = soup.select("ul > li")[2].text
book_review_rating = soup.find_all("p", class_="star-rating")[0]['class'][1]
book_img_url = "books.toscrape.com" + soup.select("img")[0]["src"].replace('../..', '')

with open('csv/book_data.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['URL', 'UPC', 'Product Type', 'Title', 'Price (incl. tax)', 'Price (excl. tax)', 'Availability', 'Description', 'Category', 'Review Rating', 'Image URL'])
    writer.writerow([book_url, book_upc, book_product_type, book_title, book_price_including_taxe, book_price_excluding_taxe, book_number_available, book_description, book_category, book_review_rating, book_img_url])