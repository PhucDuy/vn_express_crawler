
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
import datetime,time,requests
import click
from flask.cli import with_appcontext


app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_secret_key. You may change it later'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tiki.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



from scripts import web_scraper as web_scrapper

class UrlForm(FlaskForm):
    url = StringField('url', validators=[DataRequired()], render_kw={
                      "placeholder": "Search tiki products or type a tiki url!"})


@app.route('/home', methods=['GET'])
@app.route('/', methods=['GET'])
def home():
    form = UrlForm()
    form.url.data = "https://tiki.com"
    return render_template('home.html', form=form)

@app.cli.command("get_proxies")
def get_proxies():
    click.echo("get_proxies")
    web_scrapper.WebScrapper().get_proxies()
@app.cli.command("init_db")
def init_db():
    click.echo("init_db")
    db.drop_all()
    db.create_all()

@app.cli.command("load_product_from_tiki")
@with_appcontext
def load_product_from_tiki():
    click.echo("load_product_from_tiki")
    web_scrapper.WebScrapper().get_all_product_from_tiki(save_db=True)

@app.cli.command("load_category_from_tiki")
def load_from_tiki():
    click.echo("load_from_tiki")
    db.session.commit()
    web_scrapper.WebScrapper().scrape_tiki_website(app,save_db=True)


@app.route('/products', methods=('POST', 'GET'))
def product():
    form = UrlForm()
    if form.validate_on_submit():
        (df, pages) = web_scrapper.WebScrapper().scrape_from_url(form.url.data)

        return render_template(product_html, form=form, data=df, pages=pages)
    return render_template(product_html, form=form)


product_html = 'products.html'
@app.route('/products/<path:page_url>', methods=['GET', 'POST'])
def products(page_url):
    print("products page: "+page_url)
    form = UrlForm()
    if (page_url is not None):
        form.url.data = page_url
        (df, pages) = web_scrapper.WebScrapper().scrape_from_url(page_url)
        return render_template(product_html, form=form, data=df, pages=pages)

    return render_template(product_html, form=form)


@app.route('/urls')
def url():
    return "<h1>"+url_for('products', url="https://tiki.vn/search=shoe&page2")+"</h1>"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
