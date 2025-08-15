from flask import Blueprint, send_from_directory

# Create a Blueprint instance
static_route = Blueprint('static_route', __name__)

# Define a route to serve the CSV file
@static_route.route('/data/<filename>')  # Dynamic filename in the URL
def serve_file(filename):
    return send_from_directory('static/data', filename)  # Serve file from static/data directory