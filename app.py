from flask import Flask, render_template, jsonify, request
import requests
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()

OPEN_CHARGE_MAP_API_KEY = os.getenv("OPEN_CHARGE_MAP_API_KEY")
BASE_URL = "https://api.openchargemap.io/v3/poi/"

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/cars')
def cars():
    return render_template("cars.html")

@app.route('/stations')
def stations():
    return render_template("stations.html")

@app.route('/api/charging-stations/')
def get_charging_stations():
    lat = request.args.get('lat', 36.7783, type=float)  # Fetch the latitude from the query parameters or default to California's latitude
    lng = request.args.get('lng', -119.4179, type=float)  # Fetch the longitude from the query parameters or default to California's longitude
    
    params = {
        'output': 'json',
        'countrycode': 'US',
        'latitude': lat,
        'longitude': lng,
        'distance': 50,  # Fetch stations within a 50km radius of the map's center
        'distanceunit': 'KM',
        'maxresults': 100,  # Limiting to 100 results per fetch for performance
        'key': OPEN_CHARGE_MAP_API_KEY
    }
    
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        stations = response.json()
        return jsonify(stations)
    else:
        return jsonify({"error": "Failed to fetch data"}), 500


if __name__ == "__main__":
    app.run(debug=True)
