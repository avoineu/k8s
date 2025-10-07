from flask import Flask, render_template, jsonify
import socket
import os
from pymongo import MongoClient

app = Flask(__name__)

# Variables d’environnement (configurées dans le Deployment)
MONGO_USER = os.getenv("MONGO_USER", "store_admin")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "store_pass")
MONGO_HOST = os.getenv("MONGO_HOST", "mongodb")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))

# Connexion à MongoDB
client = MongoClient(f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/")
db = client["store_db"]
products_collection = db["products"]

# Liste statique de produits
products = [
    {"id": 1, "name": "T-shirt Kubernetes", "price": 20},
    {"id": 2, "name": "Mug Docker", "price": 10},
    {"id": 3, "name": "Casquette Cloud", "price": 15}
]

@app.route('/')
def home():
    hostname = socket.gethostname()
    return render_template('index.html', pod_name=hostname)

@app.route('/api/products')
def get_products():
    products = list(products_collection.find({}, {"_id": 0}))
    return jsonify(products)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)