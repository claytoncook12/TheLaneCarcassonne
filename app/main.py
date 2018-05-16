from flask import Flask, render_template, url_for, request
from flask_bootstrap import Bootstrap
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['TESTING'] = True
app.config['SECRET_KEY'] = 'hard to guess string' # Need to use environment variable
bootstrap = Bootstrap(app)
app.testing = True

# Database Setup
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    outcomes = db.relationship("Outcome", backref='player')

    def __repr__(self):
        return '<Player %r>' % self.name

class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    game_type = db.Column(db.String(100), nullable=False)
    num_players = db.Column(db.Integer, nullable=False)
    outcomes = db.relationship("Outcome", backref='game')

    def __repr__(self):
        return '<Game %r>' % self.number
    
class Outcome(db.Model):
    __tablename__ = 'outcomes'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    games_id = db.Column(db.Integer, db.ForeignKey('games.id'))
    outcome = db.Column(db.String(100), nullable=False)
    pts = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return '<Outcome %r>' % self.outcome
# End Database Setup

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/Games/<int:page_num>')
def games(page_num):
    pagination = db.session.query(Outcome,Player, Game).outerjoin(
        Player, Outcome.player_id == Player.id).outerjoin(
            Game, Outcome.games_id == Game.id).paginate(
                page=page_num,per_page=20,error_out=True)
    
    return render_template('games.html', pagination=pagination)

@app.route('/Rivalries')
def rivalries():
    return render_template('rivalries.html')

@app.route('/About')
def about():
    return render_template('about.html')

##     Error Handling Text When Ready
##@app.errorhandler(404)
##def page_not_found(e):
##    return render_template('404.html'), 404
##
##@app.errorhandler(500)
##def internal_server_error(e):
##    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
