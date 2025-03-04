# Real Estate Application in Python
import os 
import json 
import time 
from functools import cache 

import requests 
import numpy as np 
import pandas as pd 

import folium
from folium.plugins import MarkerCluster

from flask import Flask, render_template

app = Flask(__name__)

def load_and_preprocess_data(file_path="Zillow-Property-Listing-Info.csv"):
    df = pd.read_csv(file_path)
    df = df.dropna(subset=["longitude", "latitude"])

    for col in ["rentZestimate", "zestimate", "price"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["annual_rent"] = df["rentZestimate"] * 12
    df["gross_rental_yield"] = (df["annual_rent"] / df["zestimate"]) * 100
    df["gross_rental_yield"].replace([np.inf, -np.inf], np.nan, inplace=True)

    return df

data_frame = load_and_preprocess_data()

def get_marker_color(gross_yield, off_market):
    if off_market:
        return "black"
    if pd.isna(gross_yield):
        return "gray"
    if gross_yield < 5:
        return "red"
    if gross_yield < 8:
        return "orange"
    return "green"

def format_value(value, prefix="$", decimals=2):
    if pd.isna(value):
        return "N/A"
    return f"{prefix}{value:.{decimals}f}"

@app.route("/")
def index():
    if os.path.exists("templates/property_map.html"):
        return render_template("property_map.html")
    
    map_center = [data_frame["latitude"].mean(), data_frame["longitude"].mean()]
    map_ = folium.Map(location=map_center, zoom_start=12)
    marker_cluster = MarkerCluster().add_to(map_)

    for _, row in data_frame.iterrows():
        price = format_value(row["price"])
        zestimate = format_value(row["zestimate"])
        rent_zestimate = format_value(row["rentZestimate"])
        gross_yield = format_value(row["gross_rental_yield"], "%")
        bedrooms = int(row["bedrooms"]) if not pd.isna(row["bedrooms"]) else "N/A"
        bathrooms = int(row["bathrooms"]) if not pd.isna(row["bathrooms"]) else "N/A"
        living_area = int(row["livingArea"]) if not pd.isna(row["livingArea"]) else "N/A"

        try:
            street_address = json.loads(row["address"])["streetAddress"]
        except (json.JSONDecodeError, KeyError, TypeError):
            street_address = "Unknown Address"


@app.route("/price_history/<int:zpid>")
@cache
def price_history(zpid):
    url = data_frame[data_frame.zpid == zpid].url.values[0]
    api_url = "https://brightdata.com/cp/datasets/browse/gd_lfqkr8wm13ixtbd8f5?id=hl_5681f148"

    TOKEN = open("TOKEN.txt", "r").read()

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    data = [{"url": url}]

    response = requests.post(api_url, headers=headers, json=data)
    snapshot_id = response.json()["snapshot_id"]

    time.sleep(5)

    api_url = f"https://brightdata.com/cp/datasets/browse/snapshot/{snapshot_id}?format=csv"

    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    response = requests.get(api_url, headers=headers)

    if "Snapshot is empty" in response.text:
        return "No historic data"
    
    while "Snapshot is not ready yet, try again in 10s" in response.text:
        time.sleep(10)
        response = requests.get(api_url, headers=headers)
        if "Snapshot is empty" in response.text:
            return "No historic data"
        
    with open("temp.csv", "wb") as f:
        f.write(response.content)

    price_history_data_frame = pd.read_csv("temp.csv")
    price_history_data_frame = price_history_data_frame[["date", "price"]]
    price_history_data_frame["date"] = pd.to_datetime(price_history_data_frame["date"])
    price_history_data_frame["date"] = price_history_data_frame["date"].dt.strftime("%Y-%m-%d")

    return render_template("price_history.html", price_history_data_frame=price_history_data_frame)

if __name__ == "__main__":
    app.run(debug=True)