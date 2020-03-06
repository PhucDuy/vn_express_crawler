
from flask import Flask, render_template, request
from scripts.web_scraper import crawl_from_url

app = Flask(__name__)
BASE_URL = "https://tiki.vn/tivi/c5015?order=top_seller&src=c.5015.hamburger_menu_fly_out_banner"

@app.route('/')
def index():
    data = crawl_from_url(BASE_URL)

    return render_template('index.html',data=data)

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8000, debug=True)
 