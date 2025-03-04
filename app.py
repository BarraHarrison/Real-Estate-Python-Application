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

        data_frame["gross_rental_yield"] = data_frame["gross_rental_yield"].replace([np.inf, -np.inf], np.nan)

        def get_marker_color(gross_yield, off_market):
            if off_market:
                return "black"
            elif pd.isna(gross_yield):
                return "gray"
            elif gross_yield < 5:
                return "red"
            elif gross_yield < 8:
                return "orange"
            else:
                return "green"
            
        map_center = [data_frame["latitude"].mean(), data_frame["longitude"].mean()]

        map = folium.Map(location=map_center, zoom_start=12)

        marker_cluster = MarkerCluster().add_to(map)

        for idx, row in data_frame.iterrows():
            price = data_frame["price"]
            address = data_frame["address"]
            bedrooms = data_frame["bedrooms"]
            bathrooms = data_frame["bathrooms"]
            living_area = data_frame["livingArea"]
            gross_yield = data_frame["gross_rental_yield"]
            zestimate = data_frame["zestimate"]
            rent_zestimate = data_frame["rentZestimate"]
            property_url = data_frame["url"]
            zpid = data_frame["zpid"]

            if not pd.isna(price):
                price_formatted = f"${price:.2f}"
            else:
                price_formatted = "N/A"

            if not pd.isna(zestimate):
                zestimate_formatted = f"${zestimate:.2f}"
            else:
                zestimate_formatted = "N/A"

            if not pd.isna(rent_zestimate):
                rent_zestimate_formatted = f"${rent_zestimate:.2f}"
            else:
                rent_zestimate_formatted = "N/A"

            if not pd.isna(gross_yield):
                gross_yield_formatted = f"${gross_yield:.2f}"
            else:
                gross_yield_formatted = "N/A"

            bedrooms =int(bedrooms) if not pd.isna(bedrooms) else "N/A"
            bathrooms =int(bathrooms) if not pd.isna(bathrooms) else "N/A"
            living_area =int(living_area) if not pd.isna(living_area) else "N/A"

            address_dict = json.loads(address)
            street_address = address_dict["streetAddress"]

            popup_text = f"""
            <b>Address:</b> {street_address}<br>
            <b>Price:</b> {price_formatted}<br>
            <b>Bedrooms:</b> {bedrooms}<br>
            <b>Bathrooms:</b> {bathrooms}<br>
            <b>Living Area:</b> {living_area}<br>
            <b>Gross Rental Yield:</b> {gross_yield_formatted}<br>
            <b>Zestimate:</b> {zestimate_formatted}<br>
            <b>Rent Zestimate:</b> {rent_zestimate_formatted}<br>
            <a href="{property_url}" target="_blank">Zillow Link</a><br>
            <button id="button-{idx}" onclick="showLoadingAndRedirecting({idx}, '{zpid}')">Show Price History</button>
            <div id="loading-{idx}" style="display: none;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/3/3a/Gray_circles_rotate.gif" alt="loading..." width="50" height="50">
            </div>

            <script>
                function showLoadingAndRedirect(idx, zpid) {{
                    document.getElementById("button-" + idx).style.display = "none";
                    document.getElementById("loading-" + idx).style.display = "block";
                    window.location.href = "http://localhost:5000/price_history" + zpid;
                }}
            </script>
            """

            color = get_marker_color(row["gross_rental_yield"], row["isOffMarket"])

            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup=folium.Popup(folium.IFrame(popup_text, width=300, height=250)),
                icon=folium.Icon(color=color, icon="home", prefix="fa")
            ).add_to(marker_cluster)

        map.save("templates/property_map.html")
        return render_template("property_map.html")
    

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