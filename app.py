
from flask import Flask, render_template, request, redirect

from scripts.web_scraper import scrape_from_url
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
import datetime
import time

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

@app.route('/home', methods=('GET','POST'))
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)


@app.before_request
def start_timer():
    g.start = time.time()


@app.after_request
def log_request(response):
    if request.path == '/favicon.ico':
        return response
    elif request.path.startswith('/static'):
        return response

    now = time.time()
    duration = round(now - g.start, 2)
    dt = datetime.datetime.fromtimestamp(now)
    timestamp = rfc3339(dt, utc=True)

    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    host = request.host.split(':', 1)[0]
    args = dict(request.args)

    log_params = [
        ('method', request.method, 'blue'),
        ('path', request.path, 'blue'),
        ('status', response.status_code, 'yellow'),
        ('duration', duration, 'green'),
        ('time', timestamp, 'magenta'),
        ('ip', ip, 'red'),
        ('host', host, 'red'),
        ('params', args, 'blue')
    ]

    request_id = request.headers.get('X-Request-ID')
    if request_id:
        log_params.append(('request_id', request_id, 'yellow'))

    parts = []
    for name, value, color in log_params:
        part = colors.color("{}={}".format(name, value), fg=color)
        parts.append(part)
    line = " ".join(parts)

    app.logger.info(line)

    return response
