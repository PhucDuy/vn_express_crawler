
from flask import Flask, render_template, request, redirect, url_for

from scripts.web_scraper import scrape_from_url
from scripts.web_scraper import scrape_all_from_url
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
import datetime
import time
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_secret_key. You may change it later'


class UrlForm(FlaskForm):
    url = StringField('url', validators=[DataRequired()], render_kw={
                      "placeholder": "Search tiki products or type a tiki url!"})


@app.route('/home', methods=['GET'])
@app.route('/', methods=['GET'])
def home():
    form = UrlForm()
    return render_template('home.html', form=form)

@app.route('/products', methods=('POST','GET'))
def product():
    form = UrlForm()
    if form.validate_on_submit():
        (df, pages) = scrape_from_url(form.url.data)

        return render_template(product_html, form=form, data=df, pages=pages)
    return render_template(product_html, form=form)


product_html = 'products.html'
@app.route('/products/<path:page_url>', methods=['GET','POST'])
def products(page_url):
    print("products page: "+page_url)
    form = UrlForm()
    if (page_url is not None):
        form.url.data = page_url
        (df, pages) = scrape_from_url(page_url)
        return render_template(product_html, form=form, data=df, pages=pages)

    return render_template(product_html, form=form)


@app.route('/urls')
def url():
    return "<h1>"+url_for('products', url="https://tiki.vn/search=shoe&page2")+"</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
