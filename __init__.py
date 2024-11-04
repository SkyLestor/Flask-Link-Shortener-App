from flask import Flask, render_template, redirect, request
from .db import get_db
import os, random, string

app = Flask(__name__)

app.config['DB_HOST'] = os.getenv('FLASK_DB_HOST')
app.config['DB_USERNAME'] = os.getenv('FLASK_DB_USERNAME')
app.config['DB_PASSWORD'] = os.getenv('FLASK_DB_PASSWORD')
app.config['DB_DATABASE'] = os.getenv('FLASK_DB_DATABASE')


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/', defaults={'your_url' : None})
@app.route('/<your_url>')
def your_url(your_url):
    if your_url:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT original_link FROM link WHERE shortened_link = %s', (your_url,))
        result = cursor.fetchone()
        if result:
            original_link = str(result["original_link"])
            return redirect(original_link)
    return redirect('/')



@app.route('/shorten', methods=['POST'])
def shorten():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id FROM link ORDER BY id DESC LIMIT 1;")
    result = cursor.fetchone()
    new_item_id = str(result['id'] + 1) if result else '1' 

    original_link = request.form['original_link']

    if not check_if_valid_url(original_link): return redirect('/')

    shortened_link = create_random_short_url(7) + new_item_id
    cursor.execute("INSERT INTO link (original_link, shortened_link) VALUES(%s, %s)", (original_link, shortened_link))
    db.commit()
    
    return redirect('/new_link')

@app.route('/new_link')
def new_link():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT shortened_link FROM link ORDER BY id DESC LIMIT 1;")
    result = cursor.fetchone()
    if result:
        new_link = "http://127.0.0.1:5000/" + str(result["shortened_link"])
        return render_template('new_link.html', new_link=new_link)
    return redirect('/')
    


def create_random_short_url(size):
    short_url = ''.join(random.choices(string.ascii_lowercase, k=size))
    return short_url

def check_if_valid_url(url):
    if url[0] in string.punctuation: return False
    for i in url:
        if i == '.': return True
    return False


