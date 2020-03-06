from bs4 import BeautifulSoup
import requests
import pandas as pd
import re


def get_url(url):
    source = requests.get(url)
    return source


"""
Product ID = data-id
Seller ID = data-seller-product-id
Product title : data-title
Price = data-price
URL of the product image
"""

def get_product_from_soup(soup):
    products = soup.find_all('div', class_='product-item')
    product_ids = []
    seller_ids = []
    product_titles = []
    prices = []
    product_imgs = []

    for product in products:
        try:
            product_ids.append(product['data-id'])
            seller_ids.append(product['data-seller-product-id'])
            product_titles.append(product['data-title'])
            prices.append(product['data-price'])
            product_imgs.append(product.img['src'])

        except:
            pass

    product_df = pd.DataFrame({'product_id': product_ids,
                               'seller_id': seller_ids, 'title': product_titles,
                               'price': prices, 'image_url': product_imgs})
    return product_df

def crawl_from_url(url):
    response = get_url(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        link = re.search(
            r"(http|ftp|https)://([\w+?\.\w+])+([a-zA-Z0-9]*)?", url).group()
        df = get_product_from_soup(soup)
        links = [link+path for path in get_page_url(soup)]
        list_page_df = [df]
        for link in links:
            list_page_df.append(get_product_from_soup(BeautifulSoup(
                get_url(link).text, 'html.parser')))
        products_df = pd.concat(list_page_df,ignore_index=True)
        return products_df
    else:
        return None


def get_page_url(soup):
    return [li.a['href']
            for li in soup.find('div', class_='list-pager').ul.find_all('li')
            if li.a is not None and li.a['class'][0] == 'normal']





