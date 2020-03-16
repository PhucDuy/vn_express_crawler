from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import time
from app import db
import app
from scripts.models import category
from scripts.models.product import Product,Photo
from collections import deque
from lxml.html import fromstring
from itertools import cycle


from multiprocessing.pool import ThreadPool
from multiprocessing.pool import Pool
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy_session import flask_scoped_session



class WebScrapper():

    link_regex = r"(http|ftp|https)://([\w+?\.\w+])+([a-zA-Z0-9]*)?"
    web_detector_regex = r"(([--:\w?@%&+~#=]*\.[a-z]{2,4})?(\/[A-Za-z0-9-]+\/\w+))"
    tiki_search_path = "https://tiki.vn/search?q="
    parser = 'lxml'
    BASE_URL = "https://tiki.vn"
  

    def get_proxies(self):
      return ["138.68.41.90:3128","142.93.57.37:80","80.187.140.26:8080"
              "200.89.178.213:8080","41.190.33.162:8080","144.217.118.206:8080",
              "138.68.41.90:8080","198.199.120.102:8080""192.241.245.207:8080",
              "138.197.157.45:8080","138.197.157.32:8080","138.68.165.154:8080",
              "188.226.141.61:8080","95.85.36.236:8080","188.226.141.211:8080",
              "200.89.159.240:80","173.212.202.65:80","138.68.24.145:8080"]



    def get_url(self, url, delay = 1.0):
        print("GET URL: "+url)
        time.sleep(delay)
        proxy = "http://"+ next(self.proxy_pool)
        try:
            response = requests.get(url,proxies={"http": proxy} if proxy is not None else None,timeout=30)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, self.parser)
                return soup
        except Exception as err:
            print('ERROR BY REQUEST:', err)
        return None

    def get_page_url(self, soup, url, define_class):
        if soup is None:
            return None
        if url is None:
            return None
        try:
            list_pager = soup.find('div', class_='list-pager')
            if list_pager is not None:
                page_links = list_pager.ul.find('a', class_=define_class)
                if page_links is not None:
                    return url + page_links['href']
        except Exception as err:
            print(f"ERROR BY GET {define_class}: {err}")
        return None

    def get_pages(self, soup, url):
        try:
            page_links = soup.find(
                'div', class_='list-pager').ul.find_all(['span', 'a'])
            link = self.BASE_URL
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

    def get_product_from_soup(self, soup):
        products = soup.find_all('div', class_='product-item')
        product_ids = []
        seller_ids = []
        product_titles = []
        prices = []
        product_imgs = []
        urls = []
        for product in products:
            try:
                product_id = product['data-id']
                product_ids.append(product_id)
                seller_id = product['data-seller-product-id']
                seller_ids.append(seller_id)
                title = product['data-title']
                product_titles.append(title)
                price = product['data-price']
                prices.append(price)
                photo_url = product.img['src']
                product_imgs.append(photo_url)
                url = product.a['href']
                urls.append(url)

            except:
                pass

        product_df = pd.DataFrame({'product_id': product_ids,
                                   'seller_id': seller_ids, 'title': product_titles,
                                   'price': prices, 'image_url': product_imgs,
                                   "url": urls})
        return product_df

    def get_products_from_url(self, url):
        if not bool(re.match(self.web_detector_regex, url)):
            url = self.tiki_search_path+url
        soup = self.get_url(url)

        if soup is not None:
            pages = self.get_pages(soup, url)
            df = self.get_product_from_soup(soup)
            return (df, pages)
        else:
            return None

    def get_products_in_prev_and_next_page_from_url(self,category,url, func, defined_class,save_db=False):
        de = deque([url])
        while de:
            cur_url = de.popleft()
            if cur_url is None:
                break
            soup = self.get_url(cur_url)
            if soup is not None:
                df = self.get_product_from_soup(soup)
                if save_db:
                    for index, row in df.iterrows():
                      self.save_product(row,category)
                new_page = func(soup, self.BASE_URL,defined_class)
                if new_page is not None:
                    de.extend([new_page])

    def get_all_products_from_category(self, category, save_db=False):
        print("*"*20)
        print("GET PRODUCT FROM PAGE:")
        soup = self.get_url(category.url)
        print("*"*20)
        

        if soup is not None:
            df = self.get_product_from_soup(soup)
            if save_db:
                for index, row in df.iterrows():
                    self.save_product(row,category)
            prev_page = self.get_page_url(soup, self.BASE_URL, "prev")
            next_page = self.get_page_url(soup, self.BASE_URL, "next")
            # Get all previos page
            if prev_page is not None:
                self.get_products_in_prev_and_next_page_from_url(category,
                    prev_page, self.get_page_url, "prev",save_db)
            if next_page is not None:
                self.get_products_in_prev_and_next_page_from_url(category,
                    next_page, self.get_page_url, "next",save_db)
            if save_db:
              try:
                category.is_scraped = True;
                db.session.commit()
              except Exception as err:
                print(f"Error: {err}")



    def save_product(self,product_map,category):
        try:
            session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=db.engine))
            existed_product = session.query(Product).filter_by(url=product_map['url']).first()
            l_cat = session.merge(category)
            if existed_product is not None:

                existed_product.cat_ids.append(l_cat)
                session.commit()
            else:    
                photo = session.merge(Photo(url=product_map["image_url"]))
                p = session.merge(Product(product_id=product_map['product_id'],
                                        seller_id=product_map['seller_id'],
                                        title=product_map['title'], price=product_map['price'],
                                        url=product_map['url']))
                p.cat_ids.append(l_cat)
                p.image_urls.append(photo)
                
                session.add_all([p,photo])
                session.commit()
            session.remove()
        except Exception as err:
            print(f"ERROR BY SAVE PRODUCT: {err}")

    def get_main_categories(self, save_db=False):
        url = self.BASE_URL
        soup = self.get_url(url)
        result = []
        for a in soup.findAll('a', {'class': 'MenuItem__MenuLink-tii3xq-1 efuIbv'}):
            name = a.find('span', {'class': 'text'}).text
            url = re.search(self.web_detector_regex, a['href']).group()
            parent_id = None

            cat = category.Category(
                name=name, url=url, parent_id=parent_id, is_leaf_cat=False)
            if save_db:
                self.save_category(cat) 
            result.append(cat)
        return result

    def save_category(self,cat):
        if category.Category.query.filter_by(url=cat.url).first() is None:
            db.session.add(cat)
            db.session.commit()

    def get_sub_categories(self, parent_cat, save_db=False):
        url = parent_cat.url
        result = []

        try:
            soup = self.get_url(url)
            div_containers = soup.findAll(
                'div', {'class': 'list-group-item is-child'})
            for div in div_containers:
                sub_name = div.a.text
                url = div.a['href']
                sub_url = self.BASE_URL + \
                    re.search(self.web_detector_regex, url).group()
                sub_parent_id = parent_cat.id
                sub = category.Category(
                    name=sub_name, url=sub_url, parent_id=sub_parent_id, is_leaf_cat=False)
                if save_db:
                  self.save_category(sub)
                result.append(sub)
        except Exception as err:
            print('ERROR BY GET SUB CATEGORIES:', err)

        return result

    def get_all_categories(self, main_categories, save_db=False):
      
        de = deque(main_categories)
        count = 0
        while de:
            parent_cat = de.popleft()
            sub_cats = self.get_sub_categories(parent_cat, save_db=save_db)
            
            if len(sub_cats) == 0 and save_db:
                parent_cat.is_leaf_cat = True
                db.session.commit()
                # self.get_all_products_from_category(parent_cat,save_db)

            # print(sub_cats)
            de.extend(sub_cats)
            count += 1

            if count % 100 == 0:
                print(count, 'times')



    proxy_pool = None

    def scrape_tiki_website(self, save_db=False):
        proxies = self.get_proxies()
        self.proxy_pool = cycle(proxies)
        main_category = self.get_main_categories(save_db)
        self.get_all_categories(main_category,save_db)

    def get_all_product_from_tiki(self, save_db=False):
        proxies = self.get_proxies()
        self.proxy_pool = cycle(proxies)
        leaf_categories = category.Category.query.filter_by(is_leaf_cat=False,is_scraped=False).all()
        pool = ThreadPool(10)
        pool.starmap(self.get_all_products_from_category,zip(leaf_categories,[save_db] * len(leaf_categories)))        




