from flask import Flask, render_template, request
from markupsafe import escape
from urllib.parse import urlparse

import db
from models import Channel

app = Flask(__name__)
db.init_app(app)

def get_channels():
    channels = []
    with open('data/channel_ids.txt') as f:
        for line in f.readlines():
            url, rest = line.split(': ')
            _, name = rest.split(' ')[0], rest.split(' ')[1:]
            name = ' '.join(name)
            channels.append(Channel(url=url, name=name))
    return channels

def validate_submission_input(url, p1_char, p2_char, p1_tag, p2_tag, event, round, date):
    if not url:
        return "Need a URL."
    if len(url) <= 0:
        return "URL must be non-empty."
    netloc = urlparse(url).netloc
    if netloc.replace('www.', '') not in ['youtube.com', 'twitch.tv']:
        return "Only YouTube and Twitch VODs are accepted for now."
    return None

@app.route("/")
def home_page():
    latest_vods = list(db.latest_vods())
    patches = db.load_patches()
    vods = db.patch_vods(latest_vods, patches)
    return render_template("home.jinja2", vods=vods, channels=get_channels(), is_search=False)

@app.route("/search")
def search_page():
    p1 = request.args.get('p1') or ''
    p2 = request.args.get('p2') or ''
    c1 = request.args.get('c1')
    if not c1 or c1.lower() == 'any':
        c1 = ''
    c2 = request.args.get('c2')
    if not c2 or c2.lower() == 'any':
        c2 = ''
    event = request.args.get('event') or ''
    rank = request.args.get('rank')
    if not rank or rank.lower() == 'any':
        rank = ''

    search_results = list(db.search_vods(p1, p2, c1, c2, event, rank))
    patches = db.load_patches()
    vods = db.patch_vods(search_results, patches)

    return render_template("home.jinja2", vods=vods, c1=c1, c2=c2, p1=p1, p2=p2, event=event, rank=rank, channels=get_channels(), is_search=True)


@app.post("/submission")
def vod_post():
    url = escape(request.form['url']) if 'url' in request.form else None
    p1_char = escape(request.form['p1_char']) if 'p1_char' in request.form else None
    if p1_char == 'none':
        p1_char = None
    p1_tag = escape(request.form['p1_tag']) if 'p1_tag' in request.form else None
    p2_char = escape(request.form['p2_char']) if 'p2_char' in request.form else None
    if p2_char == 'none':
        p2_char = None
    p2_tag = escape(request.form['p2_tag']) if 'p2_tag' in request.form else None
    event = escape(request.form['event']) if 'event' in request.form else None
    round = escape(request.form['round']) if 'round' in request.form else None
    date = escape(request.form['date']) if 'date' in request.form else None

    error = validate_submission_input(url, p1_char, p2_char, p1_tag, p2_tag, event, round, date)
    if not error:
        db.create_submission(url, p1_char, p2_char, p1_tag, p2_tag, event, round, date)
        return render_template('submission_success.jinja2')
    return render_template('submission_fail.jinja2')
