import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin

#J'importe les dépendances et je créé la fonction qui ajoute une ligne de produit au .csv

def add_a_row(product, filename):
    with open(filename, "a", newline="", encoding="utf-8", delimiter=",") as fichier_csv :
        writer : csv.writer(fichier_csv)
        writer.writerow(product)

#^Je n'écris pas l'en-tête ici sinon elle s'écrira à chaque itération de la fonction suivante

def scrape_a_book(book_url) :
    reponse : requests.get(book_url)
    soup : BeautifulSoup(reponse.content, 'html.parser')

    product = {
        "product_page_url": book_url,
        "universal_product_code": soup.find('th', string="UPC").find_next('td').string,
        "title": soup.find("h1").text,
        "price_including_tax": soup.find("th", string="Price (incl. tax)").find_next('td').string,
        "price_excluding_tax": soup.find("th", string="Price (excl. tax)").find_next('td').string,
        "number_available": soup.find("th", string="Availability").find_next('td').string,
        "product_description": soup.find("div", {"id": "product_description"}).find_next('p').text.strip(),
        "category": soup.find("ul", class_="breadcrumb").find_all("li")[2].find("a").string,
        "review_rating": soup.find("p", class_="star-rating")["class"][1],
        "image_url": urljoin(book_url, soup.find("img")["src"])
    }

    add_a_row(list(product.values), "products.csv")

#^La ligne du dessus appelle la fonction qui ajoute une ligne avec les valeurs de chaque livre au .csv final, sous forme de liste


#Je créé la fonction qui permet d'itérer sur chaque url de chaque livre tant qu'il reste une page dans la catégorie, puis sur le bouton "next", jusqu'à ce qu'il n'y en ai plus

def scrape_category(category_url):
    while category_url :
        reponse : requests.get(category_url)
        soup : BeautifulSoup(reponse.content, "html.parser")

        books_names = soup.find_all("h3")

        for book_name in books_names :
            lien = book_name.find("a")
            if lien :
                book_url = urljoin(category_url, lien["href"])
                scrape_a_book(book_url)
        next_button = soup.find("li", class_="next")
        if next_button :
            next_page_url = urljoin(category_url, next_button.find("a")["href"])

        else :
            None
        
        category_url = next_page_url

category_url = 'http://books.toscrape.com/catalogue/category/books/mystery_3/index.html' #Je défini l'url par défaut du paramètre de la fonction scrape_category



