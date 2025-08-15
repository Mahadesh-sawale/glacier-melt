from flask import Blueprint, request, jsonify
import requests
import joblib

pdd_route = Blueprint('pdd_route', __name__)

# Fetch hourly weather data
def fetch_weather_data(lat, lon, start_date, end_date):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&hourly=temperature_2m"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching data: {response.status_code}")

# Calculate Positive Degree Days (PDD)
def calculate_pdd(weather_data):
    pdd = 0
    for temp in weather_data['hourly']['temperature_2m']:
        if temp > 0:
            pdd += temp / 24  # Average temperature contributing to PDD
    return pdd

# Estimate glacier melt percentage
def estimate_glacier_melt_percentage(pdd, melt_factor=8, max_melt=500):
    melt_mm = pdd * melt_factor
    melt_percentage = min((melt_mm / max_melt) * 100, 100)
    return melt_percentage

@pdd_route.route('/predict', methods=['POST'])
def predict_pdd():
    try:
        data = request.get_json()
        lat = data['latitude']
        lon = data['longitude']
        start_date = data['start_date']
        end_date = data['end_date']

        # Fetch weather data
        weather_data = fetch_weather_data(lat, lon, start_date, end_date)
        # Calculate PDD
        pdd = calculate_pdd(weather_data)
        # Estimate melt percentage
        melt_percentage = estimate_glacier_melt_percentage(pdd)

        # Save prediction results
        result_model = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "pdd": pdd,
            "estimated_melt_percentage": melt_percentage
        }
        joblib.dump(result_model, 'pdd_melt_prediction.pkl')

        return jsonify(result_model)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Load saved PDD model (optional route to test loading)
@pdd_route.route('/load', methods=['GET'])
def load_pdd_model():
    try:
        result_model = joblib.load('pdd_melt_prediction.pkl')
        return jsonify(result_model)
    except Exception as e:
        return jsonify({"error": str(e)}), 400