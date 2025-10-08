from flask import Flask, render_template, jsonify
import socket
import os
from pymongo import MongoClient

app = Flask(__name__)

# URI du replica set
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["store"]
products_collection = db["products"]

@app.route('/')
def home():
    hostname = socket.gethostname()
    products = list(products_collection.find({}, {"_id": 0}))
    return render_template('index.html', pod_name=hostname, products=products)

@app.route('/api/products')
def get_products():
    products = list(products_collection.find({}, {"_id": 0}))
    return jsonify(products)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)