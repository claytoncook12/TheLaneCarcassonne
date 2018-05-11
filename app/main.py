from flask import Flask, render_template, url_for
from flask_bootstrap import Bootstrap
import os

app = Flask(__name__)
app.config['TESTING'] = True
app.config['SECRET_KEY'] = 'hard to guess string' # Need to use environment variable
bootstrap = Bootstrap(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/Games')
def games():
    return render_template('games.html')

@app.route('/Rivalries')
def rivalries():
    return render_template('rivalries.html')

@app.route('/About')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
