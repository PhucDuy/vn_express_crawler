
from flask import Flask, render_template, request, redirect, url_for

from scripts.web_scraper import scrape_from_url
from scripts.web_scraper import scrape_all_from_url
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
import datetime
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_secret_key. You may change it later'


class UrlForm(FlaskForm):
    url = StringField('url', validators=[DataRequired()], render_kw={
                      "placeholder": "Please input the link for details!"})


@app.route('/home', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def home():
    form = UrlForm()
    if form.validate_on_submit():
        url = form.url.data
        (df, pages) = scrape_from_url(form.url.data)
        return redirect(url_for('products', url=url))
    return render_template('home.html', form=form)


product_html = 'products.html'
@app.route('/products/<path:url>', methods=['GET','POST'])
def products(url):
    print("products page: "+url)
    form = UrlForm()
    if (url is not None):
        form.url.data = url
        (df, pages) = scrape_from_url(url)
        return render_template(product_html, form=form, data=df, pages=pages)

    return render_template(product_html, form=form)

@app.route('/products',methods=['POST'])
def product():
    form = UrlForm()
    if form.validate_on_submit():
        (df, pages) = scrape_from_url(form.url.data)
        return render_template(product_html, form=form, data=df, pages=pages)
    return render_template(product_html, form=form)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
