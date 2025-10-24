import pandas as pd
import joblib
import pickle
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


# Load the ML model
model = joblib.load("./models/model.pkl")

# Create an API app
app = FastAPI(title="Car price prediction API", version="1.0")

# API launching test endpoint
@app.get("/health")
def health_check():
    return {"status":"healthy"}

# Define a model Metadata endpoint
@app.get("/metadata")
def model_metadata():
    return {
        "model_info": "Car Price Prediction Model",
        "model": "model.pkl",
        "version": "1.0",
        "features": [ "manufacturer", "model", "engine_size", "fuel_type", 
            "year_of_manufacture", "mileage"]
    }

# Define prediction endpoint
@app.post("/predict")
def predict_car_price(payload: dict):
    manufacturer = str(payload["Manufacturer"]).strip()
    model_name = str(payload["Model"]).strip()
    fuel = str(payload["Fuel type"]).strip()
    engine = float(payload["Engine size"])
    year = int(payload["Year of manufacture"])
    mileage = float(payload["Mileage"])

    # Derived features for training pipelines
    CURRENT_YEAR = 2025
    age = max(CURRENT_YEAR - year, 0)
    mileage_per_year = mileage / max(age, 1)
    vintage = int(age >= 20)

    # Combine all columns needed in a single-row dataframe
    row = {
        "Manufacturer": manufacturer,
        "Model": model_name,
        "Fuel type": fuel,
        "Engine size": engine,
        "Year of manufacture": year,
        "Mileage": mileage,
        "age": age,
        "mileage_per_year": mileage_per_year,
        "vintage": vintage,
    }    
    df = pd.DataFrame([row]) # Create the dataframe
    prediction = model.predict(df)[0]

    return {"predicted_price": round(float(prediction), 2)}

# Define the root endpoint
@app.get("/", response_class=HTMLResponse)
def read_root():
    html_path = os.path.join("templates","index.html")
    with open(html_path, "r") as f:
        html_content = f.read()
        return HTMLResponse(content=html_content)

""""
To pass the payload data to the code, use the following command:
curl.exe -X POST "http://127.0.0.1:8000/predict" `
-H "Content-Type: application/json" `
--data-binary (Get-Content payload.json -Raw)
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)