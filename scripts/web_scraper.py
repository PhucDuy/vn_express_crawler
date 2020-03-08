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


def get_next_page_url(soup, url):
    if soup is None:
        return None
    if url is None:
        return None
    page_links = soup.find(
        'div', class_='list-pager').ul.find('a', class_="next")
    if page_links is not None:
        return url + page_links['href']
    else:
        return None


def get_prev_page_url(soup, url):
    if soup is None:
        return None
    if url is None:
        return None
    page_links = soup.find(
        'div', class_='list-pager').ul.find('a', class_="prev")
    if page_links is not None:
        return url + page_links['href']
    else:
        return None


def get_pages(soup, url):
    try:
        page_links = soup.find('div', class_='list-pager').ul.find_all(['span', 'a'])
        link = re.search(link_regex, url).group()
        pages = []
        for page in page_links:
            data = {}
            if page.string is not None:
                data['idx'] = page.string
            elif page['class'][0] == 'next':
                data['idx'] = 'Next'
            elif page['class'][0] == 'prev':
                data['idx'] = 'Previous'
            if page.name == 'span':
                data['active'] = "enable"
                data['link'] = url
            else:
                data['active'] = ""
                data['link'] = link+page['href']

            pages.append(data)
        return pages
    except:
        return None


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


link_regex = r"(http|ftp|https)://([\w+?\.\w+])+([a-zA-Z0-9]*)?"
web_detector_regex = r"((?:https\:\/\/)|(?:http\:\/\/)|(?:www\.))?([a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(?:\??)[a-zA-Z0-9\-\._\?\,\'\/\\\+&%\$#\=~]+)"
tiki_search_path="https://tiki.vn/search?q="
parser = 'html.parser'


def scrape_from_url(url):
    if not bool(re.match(web_detector_regex,url)):
        url = tiki_search_path+url
    response = get_url(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, parser)
        pages = get_pages(soup, url)
        df = get_product_from_soup(soup)
        return (df, pages)
    else:
        return None


def scrape_all_from_url(url):
    response = get_url(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, parser)

        link = re.search(link_regex, url).group()
        df = get_product_from_soup(soup)
        list_page_df = [df]

        prev_page = get_prev_page_url(soup, url)
        next_page = get_next_page_url(soup, url)

        while (prev_page is not None):
            print(f"prev page: {prev_page}")
            response = get_url(prev_page)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                list_page_df.append(get_product_from_soup(soup))
                prev_page = get_prev_page_url(soup, link)
            else:
                prev_page = None

        while (next_page is not None):
            print(f"next page: {next_page}")
            response = get_url(next_page)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, parser)
                list_page_df.append(get_product_from_soup(soup))
                next_page = get_next_page_url(soup, link)
            else:
                next_page = None

        products_df = pd.concat(list_page_df, ignore_index=True)
        return products_df
    else:
        return None


scrape_from_url(
    'https://tiki.vn/dien-tu-dien-lanh/c4221?src=c.4221.hamburger_menu_fly_out_banner')
