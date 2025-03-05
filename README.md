# Real Estate Python Application 🏡

## Introduction 📌
This **Real Estate Python Application** is a powerful tool that helps users scout **real estate properties in New York City** using data from **Zillow via BrightData**. The application allows users to visualize property listings on an interactive map, view key details like price, Zestimate, rental yield, and even retrieve historical price data with a single click. Built with **Flask, Folium, and Pandas**, this app enables real estate investors, agents, and data enthusiasts to analyze properties efficiently.

---

## 📊 Using Zillow Data via BrightData
This project leverages **Zillow property listing data** obtained through **BrightData**. The dataset is stored in a CSV file and loaded into the application:
```python
 data_frame = pd.read_csv("Zillow-Property-Listing-Info.csv")
```
The dataset contains crucial real estate features such as:
- **zpid** (Unique property ID)
- **streetAddress** (Property address)
- **longitude & latitude** (For mapping)
- **zestimate** (Zillow estimated property value)
- **rentZestimate** (Estimated rental value)
- **price** (Current listing price)

---

## 🏗️ Data Exploration with Jupyter Notebook
Before integrating the data into the Flask application, I explored it using **Jupyter Notebook**:
```python
list(data_frame.columns)
```
This allowed me to determine which features were most relevant. I focused on:
- **Property ID (`zpid`)**
- **Location (`longitude`, `latitude`)**
- **Zillow Zestimate & RentZestimate**
- **Property pricing & rental yield**

---

## 🚀 Why Use Flask for This Application?
Flask was chosen for this project because:
✅ **Lightweight & Easy to Use** – Perfect for a small web application.
✅ **Supports Dynamic Content** – Allows interactive maps and API integration.
✅ **Great for Prototyping** – Quickly develop and test features.
✅ **Scalable** – Can be expanded into a full-stack real estate analytics tool.

---

## 🏗️ Important Functions
### **1️⃣ Data Preprocessing Function**
This function **loads and cleans** the dataset:
```python
def load_and_preprocess_data(file_path="Zillow-Property-Listing-Info.csv"):
    df = pd.read_csv(file_path)
    df = df.dropna(subset=["longitude", "latitude"])
    
    for col in ["rentZestimate", "zestimate", "price"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    df["annual_rent"] = df["rentZestimate"] * 12
    df["gross_rental_yield"] = (df["annual_rent"] / df["zestimate"]) * 100
    df["gross_rental_yield"] = df["gross_rental_yield"].replace([np.inf, -np.inf], np.nan)
    
    return df
```
### **2️⃣ Property Marker Color Function**
This function categorizes properties based on **rental yield**:
```python
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
```
### **3️⃣ Auto-Opening Browser Function**
Automatically opens the app in a browser **without manual URL input**:
```python
def open_browser():
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        time.sleep(1)
        webbrowser.open("http://127.0.0.1:5000/")
```

---

## 🔍 Extracting Data
Each property is extracted and formatted:
```python
for _, row in data_frame.iterrows():
    price = format_value(row["price"])
    zestimate = format_value(row["zestimate"])
    rent_zestimate = format_value(row["rentZestimate"])
    gross_yield = format_value(row["gross_rental_yield"], "%")
    bedrooms = int(row["bedrooms"]) if not pd.isna(row["bedrooms"]) else "N/A"
```

---

## 🏡 Creating the HTML Pop-Up
Each property has an interactive **popup** displaying relevant details:
```html
<b>Address:</b> {street_address}<br>
<b>Price:</b> {price}<br>
<b>Bedrooms:</b> {bedrooms}<br>
<b>Bathrooms:</b> {bathrooms}<br>
<b>Zestimate:</b> {zestimate}<br>
<a href="{property_url}" target="_blank">Zillow Link</a><br>
<button onclick="showLoadingAndRedirect({zpid})">Show Price History</button>
```

---

## 📈 Price History Function & TOKEN
The `price_history()` function fetches price history **from BrightData** using an API token:
```python
def price_history(zpid):
    TOKEN = open("TOKEN.txt").read().strip()
    api_url = "https://brightdata.com/..."
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(api_url, headers=headers)
```

---

## 🔧 How I Refactored the Code
Originally, functions for **data preprocessing, visualization, and API requests** were **all in one function**. Refactoring involved:
✅ **Splitting logic** into dedicated functions.
✅ **Improving code readability & maintainability**.
✅ **Eliminating redundant computations**.

---

## 🛑 Problems I Ran Into
### **1️⃣ Manual URL Entry Issue**
Initially, I had to manually enter `http://127.0.0.1:5000/` to open the app. **Fixed by adding `webbrowser.open()`**.

### **2️⃣ Two Browser Tabs Opening**
Flask's debug mode caused the browser to open **twice**. Fixed using:
```python
if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
```

### **3️⃣ Pandas `FutureWarning`**
Replaced `.replace(inplace=True)` with `df["column"] = df["column"].replace(...)` to avoid issues with future Pandas updates.

---

## 📌 Conclusion
This **Real Estate Python Application** successfully integrates **Zillow property data** and **BrightData price history** into an **interactive real estate scouting tool** for **NYC properties**. 🏙️ I personally chose to use a dataset based on NYC Real Estate Properties because I used to live in NYC on 96th st. 🗽

### 🚀 **What This Project Offers:**
✅ **Visualize NYC real estate on an interactive map**
✅ **Explore property details like Zestimate, rent, and yield**
✅ **Retrieve price history with a single click**
✅ **A lightweight and efficient Flask-based app**

This project provides **valuable insights for real estate investors** and serves as a great example of how **Python can be used in real estate analytics**. 🏡💰

