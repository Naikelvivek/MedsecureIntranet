from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB Connection
client = MongoClient('mongodb://localhost:27017/')
db = client.medsecure
doctor_collection = db.doctors
prescription_collection = db.prescriptions
modified_collection = db.modified_prescriptions

# Predefined Patient IDs
patient_ids = ['101', '102', '103', '104', '105','106', '107', '108', '109', '110']

# -------------------------- LOGIN PAGE -------------------------
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    doctor_id = request.form['doctor_id']
    password = request.form['password']

    # Fetch doctor and compare plain text password
    doctor = doctor_collection.find_one({"doctor_id": doctor_id})

    if doctor and doctor['password'] == password:  # No more hashing
        session['doctor_id'] = doctor_id
        return redirect(url_for('dashboard'))
    else:
        return "Invalid ID or Password!", 401

# -------------------------- DASHBOARD -------------------------
@app.route('/dashboard')
def dashboard():
    if 'doctor_id' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html')

# -------------------------- ADD PRESCRIPTION -------------------------
@app.route('/add_prescription', methods=['GET', 'POST'])
def add_prescription():
    if 'doctor_id' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        patient_id = request.form['patient_id']
        prescription = request.form['prescription']

        # Check if prescription already exists
        existing_prescription = prescription_collection.find_one({"patient_id": patient_id})

        if existing_prescription:
            # If it exists, modify it and add to modified_collection
            modified_collection.insert_one({
                "patient_id": patient_id,
                "prescription": prescription,
                "modified_by": session['doctor_id'],
                "modified_at": datetime.utcnow(),
                "ip_address": request.remote_addr
            })
        else:
            # Add new prescription
            prescription_collection.insert_one({
                "patient_id": patient_id,
                "prescription": prescription,
                "added_by": session['doctor_id'],
                "added_at": datetime.utcnow()
            })

        return redirect(url_for('dashboard'))

    return render_template('add_prescription.html', patient_ids=patient_ids)

# -------------------------- MODIFY PRESCRIPTION -------------------------
@app.route('/modify_prescription', methods=['GET', 'POST'])
def modify_prescription():
    if 'doctor_id' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        patient_id = request.form['patient_id']
        prescription = request.form['prescription']

        # Log modified data into modified_collection
        modified_collection.insert_one({
            "patient_id": patient_id,
            "prescription": prescription,
            "modified_by": session['doctor_id'],
            "modified_at": datetime.utcnow(),
            "ip_address": request.remote_addr
        })

        return redirect(url_for('dashboard'))

    return render_template('modify_prescription.html', patient_ids=patient_ids)

# -------------------------- FETCH PRESCRIPTIONS -------------------------
@app.route('/fetch_prescriptions', methods=['GET'])
def fetch_prescriptions():
    prescriptions = list(prescription_collection.find({}, {"_id": 0}))
    return jsonify(prescriptions)

# -------------------------- FETCH MODIFICATIONS -------------------------
@app.route('/fetch_modifications', methods=['GET'])
def fetch_modifications():
    modifications = list(modified_collection.find({}, {"_id": 0}))
    return jsonify(modifications)

# -------------------------- LOGOUT -------------------------
@app.route('/logout')
def logout():
    session.pop('doctor_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
