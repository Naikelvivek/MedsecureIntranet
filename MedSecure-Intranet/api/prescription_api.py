from flask import Flask, request, jsonify
from pymongo import MongoClient
import datetime

app = Flask(__name__)

# MongoDB Connection
client = MongoClient('mongodb://localhost:27017/')
db = client['medsecure']
prescription_collection = db['prescriptions']
modified_collection = db['modified_prescriptions']

@app.route('/add_prescription', methods=['POST'])
def add_prescription():
    data = request.json
    patient_id = data.get('patient_id')
    prescription = data.get('prescription')
    doctor_id = data.get('doctor_id')

    # Check if prescription already exists
    existing_prescription = prescription_collection.find_one({'patient_id': patient_id})

    if existing_prescription:
        # If prescription exists, modify it
        return modify_prescription(data)

    # Add new prescription
    prescription_data = {
        'patient_id': patient_id,
        'prescription': prescription,
        'doctor_id': doctor_id,
        'created_at': datetime.datetime.utcnow()
    }
    prescription_collection.insert_one(prescription_data)
    return jsonify({'message': 'Prescription added successfully!'})

@app.route('/modify_prescription', methods=['POST'])
def modify_prescription(data=None):
    if data is None:
        data = request.json

    patient_id = data.get('patient_id')
    prescription = data.get('prescription')
    doctor_id = data.get('doctor_id')

    # Update existing prescription
    prescription_collection.update_one(
        {'patient_id': patient_id},
        {'$set': {'prescription': prescription, 'modified_at': datetime.datetime.utcnow()}}
    )

    # Add modification to modified_prescriptions DB
    modified_data = {
        'patient_id': patient_id,
        'prescription': prescription,
        'modified_by': doctor_id,
        'modified_at': datetime.datetime.utcnow(),
        'ip_address': request.remote_addr
    }
    modified_collection.insert_one(modified_data)
    return jsonify({'message': 'Prescription modified and logged successfully!'})

@app.route('/fetch_prescriptions', methods=['GET'])
def fetch_prescriptions():
    prescriptions = list(prescription_collection.find({}, {'_id': 0}))
    return jsonify(prescriptions)

@app.route('/fetch_modifications', methods=['GET'])
def fetch_modifications():
    modifications = list(modified_collection.find({}, {'_id': 0}))
    return jsonify(modifications)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
