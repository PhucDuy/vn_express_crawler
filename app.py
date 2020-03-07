
from flask import Flask, render_template, request, redirect

from scripts.web_scraper import scrape_from_url
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.secret_key = 'the random string'
csrf = CSRFProtect(app)


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
        print(form.url)
        data = scrape_from_url(form.url.data)
        return render_template(home_url, form=form, data=data)
    return render_template(home_url, form=form)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
