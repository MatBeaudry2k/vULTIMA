from flask import Flask, request, jsonify
from pybaseball import statcast
import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return "🔥 PyBaseball API is live!"

@app.route('/statcast', methods=['GET'])
def get_statcast():
    start = request.args.get('start')  # Format: YYYY-MM-DD
    end = request.args.get('end')      # Format: YYYY-MM-DD

    if not start or not end:
        return jsonify({"error": "You must specify 'start' and 'end' parameters in YYYY-MM-DD format."}), 400

    try:
        data = statcast(start_dt=start, end_dt=end)
        return data.to_json(orient='records')
    except Exception as e:
        return jsonify({"error": str(e)}), 500
from flask import Flask, jsonify, request
from pybaseball import (
    statcast, statcast_pitcher, playerid_lookup, pitching_stats, batting_stats_range,
    team_game_logs, schedule_and_record, pitching_stats_bref, statcast_batter
)
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def home():
    return '🔥 PyBaseball API is live!'

@app.route('/playerid/<first>/<last>', methods=['GET'])
def get_player_id(first, last):
    try:
        result = playerid_lookup(last, first)
        return result.to_json(orient='records')
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/statcast/pitcher/<int:pitcher_id>', methods=['GET'])
def get_pitcher_statcast(pitcher_id):
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        last_month = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        data = statcast_pitcher(last_month, today, pitcher_id)
        return data.to_json(orient='records')
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/statcast/batter/<int:batter_id>', methods=['GET'])
def get_batter_statcast(batter_id):
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        last_month = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        data = statcast_batter(last_month, today, batter_id)
        return data.to_json(orient='records')
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/pitching_stats/<year>', methods=['GET'])
def get_pitching_stats(year):
    try:
        data = pitching_stats(int(year))
        return data.to_json(orient='records')
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/batting_stats_range', methods=['GET'])
def get_batting_stats_range():
    start = request.args.get('start')
    end = request.args.get('end')
    try:
        data = batting_stats_range(start, end)
        return data.to_json(orient='records')
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/team_logs/<team>/<year>', methods=['GET'])
def get_team_game_logs(team, year):
    try:
        data = team_game_logs(team, int(year))
        return data.to_json(orient='records')
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/schedule/<team>/<year>', methods=['GET'])
def get_schedule(team, year):
    try:
        data = schedule_and_record(team, int(year))
        return data.to_json(orient='records')
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/pitching_bref/<year>', methods=['GET'])
def get_pitching_stats_bref(year):
    try:
        data = pitching_stats_bref(int(year))
        return data.to_json(orient='records')
    except Exception as e:
        return jsonify({'error': str(e)})

# Statcast game-wide for recent dates
@app.route('/statcast/today', methods=['GET'])
def get_today_statcast():
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        data = statcast(yesterday, today)
        return data.to_json(orient='records')
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
