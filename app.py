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

@app.route('/charging-stations/')
def get_charging_stations():
    all_stations = []
    offset = 0
    limit = 50  # fetch 50 results at a time, but you can adjust this based on the API limits
    
    while True:
        params = {
            'output': 'json',
            'countrycode': 'US',
            'state': 'California',
            'maxresults': limit,
            'startindex': offset,
            'key': os.getenv('OPEN_CHARGE_MAP_API_KEY')
        }
        
        response = requests.get(BASE_URL, params=params)
        
        if response.status_code == 200:
            stations = response.json()
            if not stations:  # Break when no more stations are returned
                break
            all_stations.extend(stations)
            offset += limit  # Move to the next page
        else:
            return jsonify({"error": "Failed to fetch data"}), 500

    return jsonify(all_stations)



if __name__ == "__main__":
    app.run(debug=True)
