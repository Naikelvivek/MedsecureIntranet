from flask import Flask, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB Connection
client = MongoClient('mongodb://localhost:27017/')
db = client['medsecure']
modified_collection = db['modified_prescriptions']

@app.route('/fetch_modifications', methods=['GET'])
def fetch_modifications():
    modifications = list(modified_collection.find({}, {'_id': 0}))
    return jsonify(modifications)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
