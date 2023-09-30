#Importe les dépendances
import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin

#Fonction qui écrit une ligne par livre dans le .csv de sa catégorie
def add_a_row(product, filename):
    with open(filename, "a", newline="", encoding="utf-8") as fichier_csv :
        writer = csv.writer(fichier_csv)
        writer.writerow(product)

#Fonction qui extrait les informations d'un livre
def scrape_a_book(book_url) :
    reponse = requests.get(book_url)
    soup = BeautifulSoup(reponse.content, 'html.parser')

    product = {
        "product_page_url": book_url + " ",
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

    add_a_row(list(product.values()), "products.csv")

#Fonction qui itère sur toutes les pages d'une catégorie pour récupérer les infos de tous les livres
def scrape_category(category_url):
    while category_url :
        reponse = requests.get(category_url)
        soup = BeautifulSoup(reponse.content, "html.parser")

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
            next_page_url = None
        
        category_url = next_page_url

category_url = 'http://books.toscrape.com/catalogue/category/books/mystery_3/index.html'

#Écriture de l'en-tête du fichier .csv
field_names = ["product_page_url",
    "universal_product_code", 
    "title", "price_including_tax", 
    "price_excluding_tax", 
    "number_available", "product_description", 
    "category", 
    "review_rating", 
    "image_url"]

with open("products.csv", "w", newline="", encoding="utf-8") as fichier_csv:
    writer = csv.writer(fichier_csv)
    writer.writerow(field_names)

#Appel de la fonction principale
if __name__ == "__main__" :
    scrape_category(category_url)
