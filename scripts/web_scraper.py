from bs4 import BeautifulSoup
import requests
import pandas as pd


def get_url(url):
  source  = requests.get(url)
  return BeautifulSoup(source.text,'lxml')
  

"""
Product ID = data-id
Seller ID = data-seller-product-id
Product title : data-title
Price = data-price
URL of the product image
"""
def crawl_from_url(url):
  soup = get_url(url)
  products = soup.find_all('div',class_='product-item')
  product_ids = []
  seller_ids =[]
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
      
    except :
      pass

  product_df = pd.DataFrame({'product_id':product_ids, \
                            'seller_id':seller_ids,'title':product_titles, \
                            'price':prices,'image_url':product_imgs})
  return product_df