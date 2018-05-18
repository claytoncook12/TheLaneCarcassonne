from flask import Flask, render_template, url_for, request, flash, redirect
from flask_bootstrap import Bootstrap
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,IntegerField, DateTimeField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required

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
        return '{}'.format(self.name)

class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    game_type = db.Column(db.String(100), nullable=False)
    num_players = db.Column(db.Integer, nullable=False)
    outcomes = db.relationship("Outcome", backref='game')

    def __repr__(self):
        return 'Game {} on {}'.format(self.number, self.date)
    
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

# Forms Setup
def player_query():
    return Player.query.order_by(Player.name)

def game_query():
    return Game.query.order_by(Game.date.desc())

class OutcomeForm(FlaskForm):
    player_list = QuerySelectField('Name of Player:',query_factory=player_query, allow_blank=True)
    game_list = QuerySelectField('Game:',query_factory=game_query, allow_blank=True)
    outcome_input = SelectField('Outcome for Player', choices=[(
        'Win', 'Win'), ('Lose', 'Lose'), ('Tie', 'Tie')], validators=[Required()])
    pts_input = IntegerField('Points for Player',validators=[Required()])
    submit = SubmitField('Submit')

class PlayerForm(FlaskForm):
    name = StringField('Player Name:',validators=[Required()])
    submit = SubmitField('Submit')

class GameForm(FlaskForm):
    date = DateTimeField('Game was played (Format Year-Month-Day Hour:Minute)', format='%Y-%m-%d %H:%M',
                         validators=[Required()])
    num_players = IntegerField('Number of players (must be integer): ',validators=[Required()])
    submit = SubmitField('Submit')
# End Forms Setup

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/Games/<int:page_num>')
def games(page_num):
    pagination = db.session.query(Outcome,Player, Game).outerjoin(
        Player, Outcome.player_id == Player.id).outerjoin(
            Game, Outcome.games_id == Game.id).order_by(
                Game.date.desc()).order_by(
                    Game.number.desc()).order_by(
                        Outcome.pts.desc()).paginate(
                        page=page_num,per_page=20,error_out=False)
    
    return render_template('games.html', pagination=pagination)

@app.route('/Rivalries')
def rivalries():
    return render_template('rivalries.html')

@app.route('/About')
def about():
    return render_template('about.html')


@app.route('/Input', methods=['GET', 'POST'])
def input():
    form = OutcomeForm()

    return render_template('input.html', form=form)

@app.route('/Input/Player', methods=['GET', 'POST'])
def inputPlayer():
    name = None
    form = PlayerForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            name = form.name.data
            form.name.data = ''

            if db.session.query(Player).filter_by(name=name).all():
                flash('Name {} in database. Did not add the name to database.'.format(name))
                return redirect(url_for('inputPlayer'))

            else:
                # Add name to database
                addPlayer = Player(name=name)
                db.session.add(addPlayer)
                flash('Added player {}.'.format(name))
                return redirect(url_for('input'))

    return render_template('inputPlayer.html', form=form)

@app.route('/Input/Game', methods=['GET', 'POST'])
def inputGame():
    form = GameForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            date = form.date.data
            num_players = form.num_players.data

            form.date.data,form.num_players.data = '',''

            if db.session.query(Game).filter_by(date=date,num_players=num_players).all():
                flash('Game already in database')
            else:
                # Add new game to database
                addGame = Game(number=db.session.query(Game).count()+1, \
                               date=date, \
                               game_type='Carcassonne', \
                               num_players=num_players)
                db.session.add(addGame)
                flash('Added game on {}.'.format(date.strftime('%Y-%m-%d %H:%M')))
                return redirect(url_for('input'))

        else:
            flash('Error when submitting data. Check formating of inputs.')
        
    return render_template('inputGame.html', form=form)

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
