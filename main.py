import sqlite3
import time
import datetime
from flask import Flask, request, g, render_template, redirect,\
    escape, Markup, session, make_response, abort
from util.captcha import Captcha
from collections import namedtuple


DATABASE = 'data.db'
app = Flask(__name__)
app.config.from_object('settings')
Comment = namedtuple('Comment', 'name comment create_at')


def connect_db():
    return sqlite3.connect(DATABASE)


def init_db():
    conn = connect_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS comment
                 (ID INT PRIMARY KEY,
                  NAME CHAR(64) NOT NULL,
                  COMMENT TEXT NOT NULL,
                  CREATE_AT REAL NOT NULL);''')
    conn.close()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


def save_data(name, comment, create_at):
    g.db.execute(
        'INSERT INTO comment (NAME, COMMENT, CREATE_AT) VALUES (?, ?, ?)',
        (name, comment, create_at)
    )
    g.db.commit()


def load_data():
    comment_list = g.db.execute('SELECT NAME, COMMENT, CREATE_AT FROM comment').fetchall()
    return [Comment(*comment) for comment in comment_list]


@app.template_filter('nl2br')
def nl2br(s):
    return escape(s).replace('\n', Markup('<br>'))


@app.template_filter('datetime_fmt')
def datetime_fmt(t):
    dt = datetime.datetime.fromtimestamp(t)
    return dt.strftime('%Y/%m/%d %H:%M')


@app.route('/')
def index():
    data = load_data()
    return render_template('index.html', comment_list=data)


@app.route('/post', methods=['POST'])
def post():
    name = request.form.get('name')
    comment = request.form.get('comment')
    create_at = time.time()
    captcha = request.form.get('captcha')
    if Captcha.verify(captcha, session):
        save_data(name, comment, create_at)
        return redirect('/')
    abort(403)


@app.route('/captcha', methods=['GET'])
def captcha():
    img = Captcha.get(session)
    resp = make_response(img.getvalue())
    resp.headers['Content-Type'] = 'image/png'
    return resp


if __name__ == '__main__':
    init_db()
    app.run(port=8926)
