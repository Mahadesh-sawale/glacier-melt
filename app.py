import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from routes.snow_route import snow_route
from routes.pdd_route import pdd_route
from routes.seismic_route import seismic_route
from routes.register import reg
from routes.static_route import static_route

app = Flask(__name__)
CORS(app)

app.register_blueprint(snow_route, url_prefix='/snow')
app.register_blueprint(pdd_route, url_prefix='/pdd')
app.register_blueprint(seismic_route, url_prefix='/seismic')
app.register_blueprint(reg, url_prefix='/reg')
app.register_blueprint(static_route, url_prefix='/static')

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

