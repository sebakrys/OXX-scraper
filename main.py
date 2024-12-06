import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
from urllib.parse import urlparse

# Global list for  product data
products = []

def scrapeItemList(url):
    # Generate CSV filename with  timestamp and url part
    url_part = urlparse(url).path.strip("/").replace("/", "_")
    current_date = datetime.now().strftime('%Y.%m.%d_%H_%M_%S')
    csv_filename = f"itemsCatalogue_{url_part}_{current_date}.csv"

    # headers to CSV
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        headers = ['Link', 'Image', 'Title', 'Price', 'Description', 'Description HTML', 'Single Category', 'Categories']
        writer.writerow(headers)

    # get number of total pages
    response = requests.get(url)
    response.raise_for_status()
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
        response = requests.get(url + f"?page={page}")
        response.raise_for_status()
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
                with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        product.get('link', ''),
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
    # fetch product details page
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    product_details = {}

    # get description
    description_tag = soup.find('div', {'data-cy': 'ad_description'})
    if description_tag:
        product_details['description'] = description_tag.get_text(strip=True).replace("Opis", "")
        product_details['description_html'] = str(description_tag)

    # get image
    image_tag = soup.find('img', {'data-testid': 'swiper-image'})
    if image_tag:
        product_details['image'] = image_tag['src'].split(";s=")[0]+".jpg"#delete for example ";s=524x699" at end of url

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


url = "https://adaxserwis.olx.pl/home/"
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
