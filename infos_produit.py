#Importer les modules nécessaires à l'extraction des données et à l'écriture du fichier .csv

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import re

#Je spécifie directement le nom des attributs pour ne pas avoir à les répéter sans cesse, juste au cas où

field_names = ["product_page_url", 
               "universal_product_code", 
               "title", "price_including_tax", 
               "price_excluding_tax", 
               "number_available", 
               "product_description", 
               "category", 
               "review_rating", 
               "image_url"]

#Fonction d'criture des infos dans le .csv

def infos_produit(product, file_name):
    with open(file_name, "w", newline="") as fichier_csv:
        writer = csv.DictWriter(fichier_csv, fieldnames= field_names )
        writer.writeheader()
        writer.writerow(product)

#Fonction qui extrait les infos de la page

def scrap_a_book():

    url = 'http://books.toscrape.com/catalogue/i-know-what-im-doing-and-other-lies-i-tell-myself-dispatches-from-a-life-under-construction_704/index.html'
    reponse = requests.get(url)
    soup = BeautifulSoup(reponse.content, 'html.parser')

#Document parsé, plus qu'à indiquer à la fonction où aller chercher les informations

    product = {
        "product_page_url" : url,
        "universal_product_code" : soup.find('th', text= "UPC").find_next('td').text,
        "title" : soup.find("h1").text,
        "price_including_tax" : soup.find("th", text= "Price (incl. tax)").find_next('td').text,
        "price_excluding_tax" : soup.find("th", text= "Price (excl. tax)").find_next('td').text,
        "number_available" : soup.find("th", text= "Availability").find_next('td').text,
        "product_description" : soup.find("div",{"id": "product_description"}).find_next('p').text.strip(),
        "category" :soup.find('a', href =re.compile("../category/books/humor_30/index.html")).text,
        "review_rating" : soup.find("p", class_="star-rating")["class"][1],
        "image_url" : urljoin(url, soup.find("img")["src"])
    }

#Et à les écrire dans le .csv
    infos_produit(product,"product.csv")

#On appelle la fonction et le tour est joué

scrap_a_book()