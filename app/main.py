from flask import Flask, render_template, url_for, request, flash, redirect, session, g
from flask_bootstrap import Bootstrap
import os
from datetime import datetime
import re
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,IntegerField, DateTimeField, SelectField, PasswordField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required, Length, Email
from sqlalchemy import func
from sqlalchemy.sql import label
import pandas as pd

app = Flask(__name__)
app.config['TESTING'] = True
app.config['SECRET_KEY'] = 'hard to guess string' # Need to use environment variable
bootstrap = Bootstrap(app)
app.testing = True

# Login creds, Need to make environment variables
password = "password"
username = "claytoncook12@gmail.com"

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
    player_list = QuerySelectField('Name of Player:',query_factory=player_query, allow_blank=False)
    game_list = QuerySelectField('Game:',query_factory=game_query, allow_blank=False)
    outcome_input = SelectField('Outcome for Player', choices=[(
        'Win', 'Win'), ('Lose', 'Lose'), ('Tie', 'Tie')], validators=[Required()])
    pts_input = IntegerField('Points for Player',validators=[Required()])
    submit = SubmitField('Submit')

class PlayerForm(FlaskForm):
    name = StringField('Player Name:',validators=[Required()])
    submit = SubmitField('Submit')

class GameForm(FlaskForm):
    date = DateTimeField('Game was played (Format Year-Month-Day Hour:Minute)', format='%Y-%m-%d %H:%M',
                         validators=[Required("Check Format of Data Time")])
    num_players = IntegerField('Number of players (must be integer): ',validators=[Required()])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[Email("This field requires an email address"),Required(), Length(1,64),])
    password = PasswordField('Password',validators=[Required()])
    submit = SubmitField('Log In')
# End Forms Setup

# Functions
def ACAllGames():
    """All Games That Clayton Cook and Amanda Cook played in"""
    gReturnAll = db.session.query(Outcome.outcome,Outcome.pts,Player.name,Game.number,Game.date,Game.num_players).outerjoin(
            Player, Outcome.player_id == Player.id).outerjoin(
                Game, Outcome.games_id == Game.id).filter((Player.name == "Clayton Cook") | (Player.name == "Amanda Cook"))

    d = {}

    for game in gReturnAll:
            key = game[3]
            if key not in d:
                    d[key] = []
            d[key].append(game)

    for k,v in list(d.items()):
        if len(v) != 2:
            del d[k]        

    # Create List of Filtered Data
    outcomeAll = []
    for k in d.keys():
        outcomeAll.append([d[k][0][0],d[k][0][1],d[k][0][2],d[k][0][3],d[k][0][4],d[k][0][5]])
        outcomeAll.append([d[k][1][0],d[k][1][1],d[k][1][2],d[k][1][3],d[k][1][4],d[k][1][5]])

    outcomeAll.insert(0,['Outcome', 'Points', 'Name', 'Game Number', 'Date', 'Number of Players'])

    return outcomeAll

def AC1V1():
    """All Games that Clayton Cook and Amanda Cook played 1v1 in"""
    # Returns only games where players where playing
    gReturnOnly = db.session.query(Outcome.outcome,Outcome.pts,Player.name,Game.number,Game.date,Game.num_players).outerjoin(
            Player, Outcome.player_id == Player.id).outerjoin(
                Game, Outcome.games_id == Game.id).filter(
                    (Player.name == "Clayton Cook") | (Player.name == "Amanda Cook")).filter(
                        Game.num_players == 2)

    d = {}

    for game in gReturnOnly:
            key = game[3]
            if key not in d:
                    d[key] = []
            d[key].append(game)

    for k,v in list(d.items()):
        if len(v) != 2:
            del d[k]        
    # Create List of Filtered Data
    outcomeOnly = []
    for k in d.keys():
        outcomeOnly.append([d[k][0][0],d[k][0][1],d[k][0][2],d[k][0][3],d[k][0][4],d[k][0][5]])
        outcomeOnly.append([d[k][1][0],d[k][1][1],d[k][1][2],d[k][1][3],d[k][1][4],d[k][1][5]])

    outcomeOnly.insert(0,['Outcome', 'Points', 'Name', 'Game Number', 'Date', 'Number of Players'])

    return outcomeOnly

# Functions End

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/Login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            session.pop('email', None)

            if request.form['password'] == password and request.form['email'] == username: ## Need to update to use environment variable
                session['email'] = request.form['email']
                flash('Successfully login in under {}'.format(session['email']), category='alert-success')
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials', category="alert-danger")
    
    return render_template('login.html',form=form)

@app.route('/LogOut')
def logout():
    session.pop('email',None)
    return render_template('logOut.html')
    

# decarator for handling if user logged in
@app.before_request
def before_request():
    g.email = None
    if 'email' in session:
        g.email = session['email']

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
    
    # Return list of games between Clayton and Amanda 1v1
    totalCAGames = AC1V1()
    totalCAGames = pd.DataFrame(totalCAGames[1:], columns=totalCAGames[0])
    totalCAGames = totalCAGames.sort_values(['Game Number','Outcome'],ascending=[False, False])

    # Return list of games that included both Clayton and Amanda
    totalCAAll = ACAllGames()
    totalCAAll = pd.DataFrame(totalCAAll[1:], columns=totalCAAll[0])
    totalCAAll = totalCAAll.sort_values(['Game Number','Outcome'],ascending=[False, False])
    
    # Stats on Found Games 1v1
    totalCAGamesCount = len(totalCAGames['Game Number'].unique())
    totalClaytonWin = len(totalCAGames[(totalCAGames['Outcome'] == 'Win') & (totalCAGames['Name'] == 'Clayton Cook')])
    totalAmandaWin = len(totalCAGames[(totalCAGames['Outcome'] == 'Win') & (totalCAGames['Name'] == 'Amanda Cook')])
    ties = len(totalCAGames[(totalCAGames['Outcome'] == 'Tie') & (totalCAGames['Name'] == 'Amanda Cook')])
    stats1v1 = [totalCAGamesCount, totalClaytonWin, totalAmandaWin, ties]
    
    # Convert results to readable list
    totalCAGames = totalCAGames.values.tolist()
    results = totalCAGames
    
    return render_template('rivalries.html', results=results, stats1v1=stats1v1)

@app.route('/About')
def about():
    return render_template('about.html')


@app.route('/Input', methods=['GET', 'POST'])
def input():
    form = OutcomeForm()

    if g.email:
        if request.method == 'POST':
            if form.validate_on_submit():
                name = form.player_list.data
                game = form.game_list.data
                outcome = form.outcome_input.data
                pts = form.pts_input.data

                form.player_list.data,form.game_list.data,form.outcome_input.data,form.pts_input.data = '','','',''

                # Find Player and Game in Database
                findPlayer = Player.query.filter_by(name=name.name).first()
                findGame = Game.query.filter_by(number=game.number).first()

                # Add to Database
                findOutcome = Outcome.query.filter_by(player=findPlayer,game=findGame).first()
                if findOutcome == None:
                    addOutcome = Outcome(outcome=outcome,pts=pts,player=findPlayer, game=findGame)
                    db.session.add(addOutcome)
                    flash('Added {} to Game {} to database'.format(findPlayer,findGame), category="alert-success")
                else:
                    flash('Player/Game outcome already in database', category="alert-warning")

        return render_template('input.html', form=form)
    flash('Need to Login to input data.')
    return redirect(url_for('index'))
        

@app.route('/Input/Player', methods=['GET', 'POST'])
def inputPlayer():
    name = None
    form = PlayerForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            name = form.name.data
            form.name.data = ''

            if db.session.query(Player).filter_by(name=name).all():
                flash('Name {} in database. Did not add the name to database.'.format(name), category="alert-warning")
                return redirect(url_for('inputPlayer'))

            else:
                # Add name to database
                addPlayer = Player(name=name)
                db.session.add(addPlayer)
                flash('Added player {}.'.format(name), category="alert-success")
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
                flash('Game already in database', category="alert-warning")
            else:
                # Add new game to database
                addGame = Game(number=db.session.query(Game).count()+1, \
                               date=date, \
                               game_type='Carcassonne', \
                               num_players=num_players)
                db.session.add(addGame)
                flash('Added game on {}.'.format(date.strftime('%Y-%m-%d %H:%M')), category="alert-success")
                return redirect(url_for('input'))

        else:
            flash('Error when submitting data. Check formating of inputs.', category="alert-warning")
        
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
