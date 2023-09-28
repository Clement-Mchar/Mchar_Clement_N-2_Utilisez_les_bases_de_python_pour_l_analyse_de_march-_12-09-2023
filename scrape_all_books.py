import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import urllib.request
import re
import textwrap

def add_a_row(product, filename):
    with open(filename, "a", newline="", encoding="utf-8") as fichier_csv :
        writer = csv.writer(fichier_csv)
        writer.writerow(product)

def scrape_a_book(book_url, category_name) :
    reponse = requests.get(book_url)
    soup = BeautifulSoup(reponse.content, 'html.parser')

    book_title = soup.find("h1").string
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
        os.mkdir("Books_Covers")

    book_title = soup.find("h1").text
    clean_title = re.sub('[^A-Za-z0-9]+', " ", book_title).strip("'").replace("é", "e")
    max_length = 115
    shorter_title = textwrap.shorten(clean_title, width= max_length, placeholder="...")
    image_name =  f"{shorter_title}.jpg"
    image_path = os.path.join("Books_Covers", image_name)
    
    urllib.request.urlretrieve(image_url, image_path)
    
    add_a_row(list(product.values()), category_filename)    

def scrape_category(category_url):
    while category_url :
        reponse = requests.get(category_url)
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
            os.mkdir("Books")

        category_filename = os.path.join("Books", f"{category_name}.csv")

        if not os.path.exists(category_filename):
            with open(category_filename, "w", newline="", encoding="utf-8") as fichier_csv:
                writer = csv.writer(fichier_csv)
                writer.writerow(field_names)

        books_names = soup.find_all("h3")

        for book_name in books_names :
            lien = book_name.find("a")
            if lien :
                book_url = urljoin(category_url, lien["href"])
                scrape_a_book(book_url, category_name)

        next_button = soup.find("li", class_="next")
        
        if next_button :
            next_page_url = urljoin(category_url, next_button.find("a")["href"])
            category_url = next_page_url
        else :
            category_url = None

def scrape_all_books(index_url):
    reponse = requests.get(index_url)
    soup = BeautifulSoup(reponse.content, 'html.parser')

    categories = soup.select(".side_categories ul li ul li")
    category_urls = [urljoin(index_url, category.find("a")["href"]) for category in categories]
    
    for category_url in category_urls:
        scrape_category(category_url)

index_url = 'http://books.toscrape.com'

scrape_all_books(index_url)
