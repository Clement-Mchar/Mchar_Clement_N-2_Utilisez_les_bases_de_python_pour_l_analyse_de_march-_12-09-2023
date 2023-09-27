import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin



def add_a_row(product, filename):
    with open(filename, "a", newline="", encoding="utf-8") as fichier_csv :
        writer = csv.writer(fichier_csv)
        writer.writerow(product)

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
        "product_description": soup.find("div", class_="sub-header").find_next('p').text.strip(),
        "category": soup.find("ul", class_="breadcrumb").find_all("li")[2].find("a").string,
        "review_rating": soup.find("p", class_="star-rating")["class"][1],
        "image_url": urljoin(book_url, soup.find("img")["src"])
    }

    add_a_row(list(product.values()))
