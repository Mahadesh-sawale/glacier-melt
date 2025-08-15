from flask import Blueprint, request, jsonify
import pandas as pd
import joblib
import requests

snow_route = Blueprint('snow_route', __name__)

# Load the trained model
model = joblib.load('models/snow_melt_rate_model.pkl')

# Function to fetch snowfall data
def fetch_snowfall_data(latitude, longitude):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=snowfall_sum&timezone=auto"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        daily_data = data.get("daily", {})
        records = [
            {"datetime": date, "snowfall_duration": snowfall}
            for date, snowfall in zip(daily_data.get("time", []), daily_data.get("snowfall_sum", []))
        ]
        return pd.DataFrame(records)
    else:
        raise ConnectionError("Failed to fetch snowfall data.")

# Prediction route
@snow_route.route("/predict-snow", methods=["POST"])
def predict_snow():
    try:
        data = request.json
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        elevation = data.get("elevation", 8848)

        # Fetch snowfall data
        snowfall_data = fetch_snowfall_data(latitude, longitude)

        # Prepare input data
        input_data = pd.DataFrame({
            'Longitude': [longitude] * len(snowfall_data),
            'Latitude': [latitude] * len(snowfall_data),
            'Elevation': [elevation] * len(snowfall_data),
            'snowfall_duration': snowfall_data['snowfall_duration']
        })

        # Predict
        predictions = model.predict(input_data)

        # Format results
        results = [{"datetime": row["datetime"], "snow_depth": float(pred)}
                   for row, pred in zip(snowfall_data.to_dict('records'), predictions)]

        return jsonify({"predictions": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500