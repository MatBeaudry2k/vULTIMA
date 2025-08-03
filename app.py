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
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta

# pybaseball imports
from pybaseball import (
    playerid_lookup,
    statcast, statcast_pitcher, statcast_batter, statcast_batter_vs_pitcher,
    batting_stats_range, batting_stats,
    pitching_stats, pitching_stats_bref,
    team_game_logs, schedule_and_record
)

app = Flask(__name__)
CORS(app)  # allow calls from anywhere (e.g., Custom GPT)

# --------- helpers ---------
def ok(data):
    return jsonify({"ok": True, "count": (len(data) if hasattr(data, "__len__") else None), "data": data})

def bad(msg, code=400):
    return jsonify({"ok": False, "error": msg}), code

def today_str(): return datetime.utcnow().strftime("%Y-%m-%d")
def days_ago_str(n): return (datetime.utcnow() - timedelta(days=n)).strftime("%Y-%m-%d")

# --------- health ---------
@app.route("/")
def root():
    return "🔥 vULTIMA PyBaseball API up"

# --------- player / ids ---------
@app.route("/playerid")
def route_playerid():
    first = request.args.get("first")
    last = request.args.get("last")
    if not first or not last:
        return bad("Params required: ?first=First&last=Last")
    try:
        df = playerid_lookup(last, first)
        return ok(df.to_dict(orient="records"))
    except Exception as e:
        return bad(str(e), 500)

# --------- statcast raw ---------
@app.route("/statcast")
def route_statcast():
    start = request.args.get("start", days_ago_str(1))
    end = request.args.get("end", today_str())
    limit = int(request.args.get("limit", "500"))
    try:
        df = statcast(start, end)
        return ok(df.head(limit).to_dict(orient="records"))
    except Exception as e:
        return bad(str(e), 500)

@app.route("/statcast/pitcher")
def route_statcast_pitcher():
    pid = request.args.get("pitcher_id")
    if not pid: return bad("Param required: ?pitcher_id=MLBAM_ID")
    start = request.args.get("start", days_ago_str(30))
    end = request.args.get("end", today_str())
    limit = int(request.args.get("limit", "500"))
    try:
        df = statcast_pitcher(start, end, int(pid))
        return ok(df.head(limit).to_dict(orient="records"))
    except Exception as e:
        return bad(str(e), 500)

@app.route("/statcast/batter")
def route_statcast_batter():
    bid = request.args.get("batter_id")
    if not bid: return bad("Param required: ?batter_id=MLBAM_ID")
    start = request.args.get("start", days_ago_str(30))
    end = request.args.get("end", today_str())
    limit = int(request.args.get("limit", "500"))
    try:
        df = statcast_batter(start, end, int(bid))
        return ok(df.head(limit).to_dict(orient="records"))
    except Exception as e:
        return bad(str(e), 500)

@app.route("/bvp")
def route_bvp():
    batter_id = request.args.get("batter_id")
    pitcher_id = request.args.get("pitcher_id")
    if not batter_id or not pitcher_id:
        return bad("Params required: ?batter_id= &pitcher_id=")
    try:
        df = statcast_batter_vs_pitcher(int(batter_id), int(pitcher_id))
        return ok(df.to_dict(orient="records"))
    except Exception as e:
        return bad(str(e), 500)

# --------- summarized helpers for betting ---------
@app.route("/pitchmap")
def route_pitchmap():
    """Aggregated pitch mix & results for a pitcher over a date window."""
    pid = request.args.get("pitcher_id")
    if not pid: return bad("Param required: ?pitcher_id=")
    start = request.args.get("start", days_ago_str(30))
    end = request.args.get("end", today_str())
    try:
        df = statcast_pitcher(start, end, int(pid))
        if df.empty: return ok([])
        grp = df.groupby("pitch_name").agg(
            pitches=("pitch_name", "count"),
            avg_velo=("release_speed", "mean"),
            whiff_pct=("description", lambda s: (s.str.contains("swinging_strike|swinging_strike_blocked", case=False, na=False).sum() / len(s))*100),
            called_strike_pct=("description", lambda s: (s.str.contains("called_strike", case=False, na=False).sum() / len(s))*100),
            avg_launch_speed=("launch_speed", "mean"),
            avg_launch_angle=("launch_angle", "mean"),
            xwoba=("estimated_woba_using_speedangle", "mean")
        ).reset_index().sort_values("pitches", ascending=False)
        return ok(grp.round(3).to_dict(orient="records"))
    except Exception as e:
        return bad(str(e), 500)

@app.route("/whiff_rates")
def route_whiff():
    pid = request.args.get("pitcher_id")
    if not pid: return bad("Param required: ?pitcher_id=")
    start = request.args.get("start", days_ago_str(30))
    end = request.args.get("end", today_str())
    try:
        df = statcast_pitcher(start, end, int(pid))
        if df.empty: return ok([])
        grp = df.groupby("pitch_name").apply(
            lambda g: (g["description"].str.contains("swinging_strike", case=False, na=False) |
                       g["description"].str.contains("swinging_strike_blocked", case=False, na=False)).mean()*100
        ).reset_index(name="whiff_pct")
        return ok(grp.round(2).to_dict(orient="records"))
    except Exception as e:
        return bad(str(e), 500)

# --------- seasonal/team info ---------
@app.route("/batting_stats_range")
def route_batting_range():
    start = request.args.get("start")
    end = request.args.get("end")
    if not start or not end: return bad("Params required: ?start=YYYY-MM-DD&end=YYYY-MM-DD")
    try:
        df = batting_stats_range(start, end)
        return ok(df.to_dict(orient="records"))
    except Exception as e:
        return bad(str(e), 500)

@app.route("/batting_stats/<int:year>")
def route_batting_year(year):
    try:
        df = batting_stats(year)
        return ok(df.to_dict(orient="records"))
    except Exception as e:
        return bad(str(e), 500)

@app.route("/pitching_stats/<int:year>")
def route_pitching_year(year):
    try:
        df = pitching_stats(year)
        return ok(df.to_dict(orient="records"))
    except Exception as e:
        return bad(str(e), 500)

@app.route("/pitching_bref/<int:year>")
def route_pitching_bref(year):
    try:
        df = pitching_stats_bref(year)
        return ok(df.to_dict(orient="records"))
    except Exception as e:
        return bad(str(e), 500)

@app.route("/team_logs")
def route_team_logs():
    team = request.args.get("team")  # e.g., 'LAD'
    year = request.args.get("year", datetime.utcnow().year)
    if not team: return bad("Param required: ?team=TEAM_ABBR (e.g., LAD)")
    try:
        df = team_game_logs(team, int(year))
        return ok(df.to_dict(orient="records"))
    except Exception as e:
        return bad(str(e), 500)

@app.route("/schedule")
def route_schedule():
    team = request.args.get("team")  # e.g., 'LAD'
    year = request.args.get("year", datetime.utcnow().year)
    if not team: return bad("Param required: ?team=TEAM_ABBR")
    try:
        df = schedule_and_record(team, int(year))
        return ok(df.to_dict(orient="records"))
    except Exception as e:
        return bad(str(e), 500)

# --------- simple betting utilities (placeholders to wire to OddsJam later) ---------
@app.route("/nrfi_predict")
def route_nrfi():
    """Toy indicator combining SP whiff & recent offense to suggest NRFI/YRFI."""
    home_pid = request.args.get("home_pitcher_id")
    away_pid = request.args.get("away_pitcher_id")
    if not home_pid or not away_pid:
        return bad("Params required: ?home_pitcher_id=&away_pitcher_id=")
    try:
        # pull last-30 for both pitchers; compute crude K indicator
        def k_indicator(pid):
            df = statcast_pitcher(days_ago_str(30), today_str(), int(pid))
            if df.empty: return 0
            swings = df["description"].str.contains("swinging_strike", case=False, na=False) | \
                     df["description"].str.contains("swinging_strike_blocked", case=False, na=False)
            return float(swings.mean()*100)
        home_k = k_indicator(home_pid)
        away_k = k_indicator(away_pid)
        nrfi_prob = min(0.93, max(0.07, (home_k + away_k)/200))  # crude 0–1
        return ok({
            "home_pitcher_whiff_pct": round(home_k,2),
            "away_pitcher_whiff_pct": round(away_k,2),
            "model_nrfi_prob": round(nrfi_prob,3),
            "model_yrfi_prob": round(1-nrfi_prob,3),
            "recommendation": "NRFI" if nrfi_prob >= 0.55 else ("YRFI" if nrfi_prob <= 0.45 else "Pass")
        })
    except Exception as e:
        return bad(str(e), 500)

@app.route("/line-movement")
def route_line_movement():
    # To be replaced with OddsJam action inside GPT; placeholder structure
    game = request.args.get("game", "TBD")
    return ok({"game": game, "open": -120, "current": -138, "note": "Steam toward favorite [DEMO]"} )

@app.route("/value-bets")
def route_value_bets():
    # Placeholder; your GPT should pull OddsJam +EV and merge with these data
    demo = [
        {"matchup": "ATL vs NYM", "bet": "NRFI", "odds": -120, "edge_pct": 4.1},
        {"matchup": "LAD vs ARI", "bet": "Alt K: Gallen 5+", "odds": -150, "edge_pct": 3.6}
    ]
    return ok(demo)

# --------- convenience ---------
@app.route("/statcast/today")
def route_statcast_today():
    start = days_ago_str(1); end = today_str()
    try:
        df = statcast(start, end)
        return ok(df.head(500).to_dict(orient="records"))
    except Exception as e:
        return bad(str(e), 500)

if __name__ == "__main__":
    app.run()
