# No more need for hashlib
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.medsecure

# Collections
doctor_collection = db.doctors
prescription_collection = db.prescriptions
modified_collection = db.modified_prescriptions
