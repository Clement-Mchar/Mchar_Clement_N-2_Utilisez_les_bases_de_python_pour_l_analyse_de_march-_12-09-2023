import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import urllib.request
import re
import textwrap
from concurrent.futures import ThreadPoolExecutor

#Fonction qui écrit une ligne par livre dans le .csv de sa catégorie
def add_a_row(product, filename):
    with open(filename, "a", newline="", encoding="utf-8") as fichier_csv :
        writer = csv.writer(fichier_csv)
        writer.writerow(product)

#Fonction qui extrait les informations d'un livre
def scrape_a_book(book_url, category_name) :
    reponse = requests.get(book_url)
    soup = BeautifulSoup(reponse.content, 'html.parser')

    book_title = soup.find("h1").text
    image_url = urljoin(book_url, soup.find("img")["src"])

    product = {
        "product_page_url": book_url + " ",
        "universal_product_code": soup.find('th', string="UPC").find_next('td').string,
        "title": book_title,
        "price_including_tax": soup.find("th", string="Price (incl. tax)").find_next('td').string,
        "price_excluding_tax": soup.find("th", string="Price (excl. tax)").find_next('td').string,
        "number_available": soup.find("th", string="Availability").find_next('td').string,
        "product_description": soup.find("div", class_="sub-header").find_next('p').text.strip(),
        "category": category_name,
        "review_rating": soup.find("p", class_="star-rating")["class"][1],
        "image_url": image_url
    }

    if not os.path.exists("Books"):
        os.mkdir("Books")

    category_filename = os.path.join("Books", f"{category_name}.csv")
    
    if not os.path.exists("Books_Covers") :
        os.mkdir("Books_Covers") #Créé un dossier "Books_Covers"

    clean_title = re.sub('[^A-Za-z0-9]+', " ", book_title).strip("'")
    max_length = 115
    shorter_title = textwrap.shorten(clean_title, width= max_length, placeholder="...")
    image_name =  f"{shorter_title}.jpg"
    image_path = os.path.join("Books_Covers", image_name) #Formate les titres des livres pour éviter les erreurs
    
    urllib.request.urlretrieve(image_url, image_path) #Télécharge l'image de chaque livre dans le dossier "Books_Covers"
    
    add_a_row(list(product.values()), category_filename)    

#Fonction qui itère sur toutes les pages d'une catégorie pour récupérer les infos de tous les livres
def scrape_category(category_page):
    while category_page :
        reponse = requests.get(category_page)
        soup = BeautifulSoup(reponse.content, "html.parser")

        category_name = soup.find("ul", class_="breadcrumb").find_all("li")[-1].string.strip()

        field_names = [
            "product_page_url", 
            "universal_product_code", 
            "title", 
            "price_including_tax",
            "price_excluding_tax",
            "number_available", 
            "product_description", 
            "category",
            "review_rating", 
            "image_url"
            ]
        
        if not os.path.exists("Books"):
            os.mkdir("Books") #Créé un dossier "Books"

        category_filename = os.path.join("Books", f"{category_name}.csv")

        if not os.path.exists(category_filename):
            with open(category_filename, "w", newline="", encoding="utf-8") as fichier_csv:
                writer = csv.writer(fichier_csv)
                writer.writerow(field_names) #Créé un fichier .csv avec une en-tête par catégorie

        books_names = soup.find_all("h3")

        for book_name in books_names :
            lien = book_name.find("a")
            if lien :
                book_url = urljoin(category_page, lien["href"])
                scrape_a_book(book_url, category_name)

        next_button = soup.find("li", class_="next")
        
        if next_button :
            next_page_url = urljoin(category_page, next_button.find("a")["href"])
            category_page = next_page_url
        else :
            category_page = None

#Fonction qui itère sur toutes les catégories
def scrape_all_books(index_url):
    reponse = requests.get(index_url)
    soup = BeautifulSoup(reponse.content, 'html.parser')

    categories = soup.select(".side_categories ul li ul li")
    category_urls = [urljoin(index_url, category.find("a")["href"]) for category in categories]
    
    with ThreadPoolExecutor(max_workers=200) as executor:
        executor.map(scrape_category, category_urls) #Accélère l'extraction des données

index_url = 'http://books.toscrape.com'

if __name__ == "__main__" :
    scrape_all_books(index_url)

