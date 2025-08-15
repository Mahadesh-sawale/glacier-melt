import pandas as pd
from flask import Blueprint, request, jsonify
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime, timedelta

# Flask app initialization
seismic_route = Blueprint('seismic_route', __name__)

# Load model, scaler, and max_y_train
MODEL_PATH = "models/model.joblib"
SCALER_PATH = "models/scaler.joblib"
MAX_Y_PATH = "models/max_y_train.joblib"

try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    max_y_train = joblib.load(MAX_Y_PATH)
    print("Model, scaler, and max_y_train loaded successfully.")
except FileNotFoundError:
    print("Trained model not found. Please ensure the model is trained and saved properly.")
    model, scaler, max_y_train = None, None, None

def fetch_magnitude_from_api(lat, lon):
    """Fetch the magnitude from the USGS Earthquake API."""
    try:
        import requests
        base_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=7)
        params = {
            "format": "geojson",
            "latitude": lat,
            "longitude": lon,
            "maxradiuskm": 50,
            "starttime": start_time.isoformat(),
            "endtime": end_time.isoformat(),
        }
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        if data["features"]:
            mag = data["features"][0]["properties"]["mag"]
            return mag
        else:
            return 5.0  # Default magnitude if no data is found
    except Exception as e:
        print(f"Error fetching magnitude from API: {e}")
        return 5.0  # Default magnitude in case of an error

@seismic_route.route('/predict', methods=['POST'])
def predict_melt_rate():
    """Predict glacier melt rate based on latitude and longitude."""
    if not model or not scaler or max_y_train is None:
        return jsonify({"error": "Model not loaded. Please train the model first."}), 500

    # Get latitude and longitude from the JSON body
    try:
        data = request.get_json()
        lat = float(data.get('lat'))
        lon = float(data.get('lon'))
    except (ValueError, TypeError, KeyError):
        return jsonify({"error": "Invalid or missing latitude and longitude parameters."}), 400

    # Fetch magnitude using the API or default
    mag = fetch_magnitude_from_api(lat, lon)
    depth_km = 10.0  # Default depth
    now = datetime.now()
    year, month, day = now.year, now.month, now.day

    # Create input data for the model
    user_data = pd.DataFrame({
        'LAT': [lat],
        'LON': [lon],
        'MAG': [mag],
        'DEPTHkm': [depth_km],
        'year': [year],
        'month': [month],
        'day': [day]
    })

    # Scale the input data
    user_data_scaled = scaler.transform(user_data)

    # Predict melt rate
    predicted_melt_rate = model.predict(user_data_scaled)

    # Normalize predictions to percentage
    predicted_melt_rate_percent = (predicted_melt_rate / max_y_train) * 100
    predicted_melt_rate_percent = predicted_melt_rate_percent.round().astype(int)

    # Return the prediction as a JSON response
    return jsonify({
        "latitude": lat,
        "longitude": lon,
        "predicted_melt_rate_percent": int(predicted_melt_rate_percent[0])
    })