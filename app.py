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
from folium import MacroElement

from flask import Flask, render_template, request

app = Flask(__name__)

data_frame = pd.read_csv("Zillow-Property-Listing-Info.csv")

@app.route("/")
def index():
    global data_frame

    if os.path.exists("templates/property_map.html"):
        return render_template("property_map.html")
    else:
        data_frame = data_frame.dropna(subset=["longitude", "latitude"])

        data_frame["rentZestimate"] = pd.to_numeric(data_frame["rentZestimate"], errors="coerce")
        data_frame["zestimate"] = pd.to_numeric(data_frame["zestimate"], errors="coerce")
        data_frame["price"] = pd.to_numeric(data_frame["price"], errors="coerce")

        data_frame["annual_rent"] = data_frame["rentZestimate"] * 12
        data_frame["gross_rental_yield"] = (data_frame["annual_rent"] / data_frame["zestimate"]) * 100
        