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

def get_marker_color():
    pass

def format_value():
    pass

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