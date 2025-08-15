from flask import Flask, request, jsonify, Blueprint
import csv

reg = Blueprint('reg', __name__)
@reg.route('/save', methods=['POST'])
def submit():
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    glacier = data.get('glacier')
    # Write the data to a CSV file
    with open('user_data.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, phone, glacier])

    return jsonify({"message": "Data saved successfully!"})