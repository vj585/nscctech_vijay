from flask import Flask, request, redirect, render_template, flash
import sqlite3
import string
import random
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  

# Database setup
def init_db():
    if not os.path.exists('url_shortener.db'):
        conn = sqlite3.connect('url_shortener.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS urls
                     (id INTEGER PRIMARY KEY, short_url TEXT, original_url TEXT)''')
        conn.commit()
        conn.close()
        print("Database initialized.")

# Generate a random short URL
def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for _ in range(6))
    return short_url

# Get original URL from the database
def get_original_url(short_url):
    try:
        conn = sqlite3.connect('url_shortener.db')
        c = conn.cursor()
        c.execute("SELECT original_url FROM urls WHERE short_url=?", (short_url,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        print(f"Error fetching original URL: {e}")
        return None

def store_url(short_url, original_url):
    try:
        conn = sqlite3.connect('url_shortener.db')
        c = conn.cursor()
        c.execute("INSERT INTO urls (short_url, original_url) VALUES (?, ?)", (short_url, original_url))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error storing URL: {e}")

# Route to the homepage
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['original_url']
        if not original_url:
            flash("Please provide a valid URL.")
            return redirect('/')
        
        short_url = generate_short_url()
        store_url(short_url, original_url)
        
        flash(f"Shortened URL is: {request.host_url}{short_url}")
        return redirect('/')
    return render_template('index.html')

# Redirect to original URL
@app.route('/<short_url>')
def redirect_to_url(short_url):
    original_url = get_original_url(short_url)
    if original_url:
        return redirect(original_url)
    else:
        return "URL not found", 404

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)
