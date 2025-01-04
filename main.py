import os
import re
import time

import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
from urllib.parse import urlparse

# Global list for  product data
products = []
def createFileAndAddHeaders(filename):
    # headers to CSV
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        headers = ['ID', 'Short description', 'Images', 'Title', 'Price', 'Description NoHTML', 'Description', 'Single Category', 'Categories']
        writer.writerow(headers)



def fetch_with_retries(url, retries=3, delay=2):
    """
    Pobiera dane z podanego URL z mechanizmem ponawiania prób w przypadku błędów HTTP.
    :param url: URL do pobrania
    :param retries: Maksymalna liczba prób
    :param delay: Opóźnienie między próbami (w sekundach)
    :return: Odpowiedź HTTP (response) lub None
    """
    for attempt in range(1, retries + 1):
        try:
            if(attempt>1):
                print(f"Fetching URL: {url} (Attempt {attempt}/{retries})")
            response = requests.get(url)
            response.raise_for_status()  # Wyjątek, jeśli status >= 400
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            if attempt < retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Maximum retries reached. Skipping.")
                return None

def scrapeItemList(url):
    # Generate CSV filename with  timestamp and url part
    url_part = urlparse(url).path.strip("/").replace("/", "_")
    current_date = datetime.now().strftime('%Y.%m.%d_%H_%M_%S')
    part = 0
    csv_filename = f"itemsCatalogue_{url_part}_{current_date}"
    print("File Part: " + str(part))

    # create file and add headers
    createFileAndAddHeaders(csv_filename+"_part"+str(part)+".csv")

    # get number of total pages
    response = fetch_with_retries(url,retries=5, delay=5)
    if not response:
        print(f"Skipping URL {url} due to repeated failures.")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    pagination_items = soup.find_all('li', {'data-testid': 'pagination-list-item'})
    try:
        last_page = max(int(item.get_text()) for item in pagination_items if item.get_text().isdigit())
    except:
        last_page = 1

    print(f"Found {last_page} pages to scrape.")

    # search through all pages(pagination)
    for page in range(1, last_page + 1):
        print(f"Scraping page {page}...")
        response = fetch_with_retries(url + f"?page={page}", retries=5, delay=5)
        if not response:
            print(f"Skipping page {page} due to repeated failures.")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # find all product cards on the current page
        product_cards = soup.find_all('div', {'data-cy': 'l-card'})

        # extract data from each product card
        for card in product_cards:
            product = {}
            link_tag = card.find('a', {'class': 'css-1bye945'})
            if link_tag:
                product_url = link_tag['href']
                product['link'] = product_url

                # fetch details for the product
                detailed_info = scrapeItemDetails(product_url)
                if detailed_info:
                    product.update(detailed_info)


            title_tag = card.find('p', {'class': 'css-ki4ei7'})
            if title_tag:
                product['title'] = title_tag.get_text(strip=True)


            price_tag = card.find('span', {'data-testid': 'ad-price'})
            if price_tag:
                product['price'] = price_tag.get_text(strip=True)

            # save product data to CSV
            if product:
                print(f"Saving: {product['title']}")
                if(os.path.getsize(csv_filename + "_part" + str(part) + ".csv")>2000000):
                    part+=1
                    createFileAndAddHeaders(csv_filename + "_part" + str(part) + ".csv")
                    print("new File Part: "+str(part))

                with open(csv_filename + "_part" + str(part) + ".csv", mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        product.get('ID', ''),
                        product.get('link', '').replace("x", "&#120;"),
                        product.get('image', ''),
                        product.get('title', ''),
                        product.get('price', ''),
                        product.get('description', ''),
                        product.get('description_html', ''),
                        product.get('categories', [])[1],
                        ', '.join(product.get('categories', []))
                    ])
                products.append(product)

def scrapeItemDetails(url):
    response = fetch_with_retries(url, retries=5, delay=5)
    if not response:
        print(f"Skipping product details for URL {url} due to repeated failures.")
        return {}

    soup = BeautifulSoup(response.text, 'html.parser')

    product_details = {}

    # get description
    description_tag = soup.find('div', {'data-cy': 'ad_description'})
    if description_tag:
        product_details['description'] = re.sub(r"\+48\*{7}\d{2}", "", description_tag.get_text(strip=True).replace("Opis", "")) # re.sub(r"\+48\*{7}\d{2}", "", text) - deleting for example telephone +48*******75
        found_tel = re.findall(r"\+48\*{7}\d{2}", str(description_tag).replace("Opis", ""))
        if(found_tel):
            print("nr tel:", found_tel)
        product_details['description_html'] = re.sub(r"\+48\*{7}\d{2}", "", str(description_tag).replace("Opis", ""))

    # get image
    image_tag = soup.find('img', {'data-testid': 'swiper-image'})
    if image_tag:
        product_details['image'] = image_tag['src'].split(";s=")[0]+".jpg"#delete for example ";s=524x699" at end of url

    # get ID
    id_tag = soup.find('span', {'class': 'css-12hdxwj'})
    if image_tag:
        product_details['ID'] = id_tag.get_text(strip=True).replace("ID:", "")

    # get categories from breadcrumbs
    breadcrumbs = soup.find('ol', {'data-testid': 'breadcrumbs'})
    if breadcrumbs:
        categories = []
        breadcrumb_items = breadcrumbs.find_all('li', {'data-testid': 'breadcrumb-item'})
        for item in breadcrumb_items:
            category_text = item.get_text(strip=True)
            if "Strona główna".lower() in category_text.lower():  # pomin dla Strona główna
                continue
            if "Opolskie".lower() in category_text.lower():  # "Opolskie" - zakoncz na wojewodztwie
                break
            categories.append(category_text)
        product_details['categories'] = categories

    return product_details


url = ""#base url, for example: https://shop***.olx.pl/home/motoryzacja/
scrapeItemList(url)

# display the results
for i, product in enumerate(products, start=1):
    print(f"Product {i}:")
    print(f"  Link: {product.get('link')}")
    print(f"  Image: {product.get('image')}")
    print(f"  Title: {product.get('title')}")
    print(f"  Price: {product.get('price')}")
    print(f"  Description: {product.get('description')}")
    print(f"  Categories: {product.get('categories')}")
    print("-" * 40)
