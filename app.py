from flask import Flask, render_template, jsonify, request
import requests
from dotenv import load_dotenv
import os
from flask_bootstrap import Bootstrap
import plotly.graph_objs as go
import pandas as pd
import json
import plotly


app = Flask(__name__)
bootstrap = Bootstrap(app)
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


@app.route('/sources')
def sources():
    return render_template('sources.html')


@app.route('/api/charging-stations/')
def get_charging_stations():
    lat = request.args.get('lat', 36.7783, type=float)  # Default to California's coordinates
    lng = request.args.get('lng', -119.4179, type=float)

    params = {
        'output': 'json',
        'countrycode': 'US',
        'maxresults': 50,
        'latitude': lat,
        'longitude': lng,
        'key': OPEN_CHARGE_MAP_API_KEY
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        stations = response.json()
        return jsonify(stations)
    else:
        return jsonify({"error": "Failed to fetch data"}), 500

@app.route('/charts')
def charts():
    # Your data loading 
    df = pd.read_csv('data/cleaned_data.csv')

    top_states_ev = df[df['Year'] == 2022].sort_values(by='Electric (EV)', ascending=False).head(11)
    top_states_ev = top_states_ev[top_states_ev['State'] != 'United States'].head(10)


    # Process the data for the pie chart
    year_data = df[df['Year'] == 2022].sum(numeric_only=True)
    year_data = year_data.drop('Year')

    # Create pie chart with Plotly
    fuel_data = [go.Pie(labels=year_data.index, values=year_data.values, hole=.3)]
    fuel_layout = go.Layout(title='Fuel Type Distribution for 2022')
    fuel_chart = go.Figure(data=fuel_data, layout=fuel_layout)

    # Top 10 States with EVs
    ev_data = [go.Bar(x=top_states_ev['State'], y=top_states_ev['Electric (EV)'])]
    ev_layout = go.Layout(title='Top 10 States with Electric Vehicles in 2022')
    ev_chart = go.Figure(data=ev_data, layout=ev_layout)

    # Growth of EVs in California over the years
    ca_ev_growth = df[df['State'] == 'California'][['Year', 'Electric (EV)']]
    ev_growth_data = go.Scatter(x=ca_ev_growth['Year'], y=ca_ev_growth['Electric (EV)'], mode='lines+markers', name='EVs in California')
    ev_growth_layout = go.Layout(title='Growth of Electric Vehicles in California Over the Years')
    ev_growth_chart = go.Figure(data=[ev_growth_data], layout=ev_growth_layout)

    # Growth of Electric Vehicles Over the Years
    all_ev_growth = df.groupby('Year')['Electric (EV)'].sum().reset_index()
    all_ev_growth_data = go.Scatter(x=all_ev_growth['Year'], y=all_ev_growth['Electric (EV)'], mode='lines+markers', name='EVs Growth Over Years')
    all_ev_growth_layout = go.Layout(title='Growth of Electric Vehicles Over the Years')
    all_ev_growth_chart = go.Figure(data=[all_ev_growth_data], layout=all_ev_growth_layout)

    #Comparison of Traditional vs Alternative Fuel for 2022
    fuel_data_2022 = df[df['Year'] == 2022].sum(numeric_only=True)
    fuel_data_2022 = fuel_data_2022.drop('Year')

    traditional_fuel = fuel_data_2022.get('Gasoline', 0)
    alternative_fuel = fuel_data_2022.sum() - traditional_fuel

    comp_data = [go.Bar(x=['Traditional', 'Alternative'], y=[traditional_fuel, alternative_fuel])]
    comp_layout = go.Layout(title='Comparison of Traditional vs Alternative Fuel for 2022')
    comp_chart = go.Figure(data=comp_data, layout=comp_layout)

    #Comparison of EV vs. HEV vs. Diesel in 2022 for all States
    statewise_data_2022 = df[df['Year'] == 2022]

    ev_data_statewise = go.Bar(x=statewise_data_2022['State'], y=statewise_data_2022['Electric (EV)'], name='EV')
    hev_data_statewise = go.Bar(x=statewise_data_2022['State'], y=statewise_data_2022['Hybrid Electric (HEV)'], name='HEV')
    diesel_data_statewise = go.Bar(x=statewise_data_2022['State'], y=statewise_data_2022['Diesel'], name='Diesel')

    statewise_layout = go.Layout(title='Comparison of EV vs. HEV vs. Diesel in 2022 for all States', barmode='group')
    statewise_chart = go.Figure(data=[ev_data_statewise, hev_data_statewise, diesel_data_statewise], layout=statewise_layout)



    return render_template('charts.html', 
                       fuel_chart=fuel_chart.to_html(), 
                       ev_chart=ev_chart.to_html(), 
                       ev_growth_chart=ev_growth_chart.to_html(),
                       all_ev_growth_chart=all_ev_growth_chart.to_html(),
                       comp_chart=comp_chart.to_html(),
                       statewise_chart=statewise_chart.to_html())



if __name__ == "__main__":
    app.run(debug=True)
