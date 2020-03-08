
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
    url = StringField('url', validators=[DataRequired()])


home_url = 'index.html'
@app.route('/', methods=('GET', 'POST'))
def index():
    form = UrlForm()
    if request.method == 'POST':
        return search_products(form)
    return render_template(home_url, form=form)


def search_products(form):
    if form.validate_on_submit():
        (df, pages) = scrape_from_url(form.url.data)
        return render_template(home_url, form=form, data=df, pages=pages)
    return render_template(home_url, form=form)


@app.route('/load_new_page/', methods=['POST'])
def load_new_page():
    form = UrlForm()
    return redirect(url_for('/', form=form))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
