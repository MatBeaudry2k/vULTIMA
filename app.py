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
