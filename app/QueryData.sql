select name, date, game_type, number, outcome, pts, num_players 
from outcomes
inner join players on players.id = outcomes.player_id
inner join games on games.id = outcomes.games_id;

