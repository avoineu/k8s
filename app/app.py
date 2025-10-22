from flask import Flask, render_template, jsonify
import socket
import os
import json
from pymongo import MongoClient
import redis

app = Flask(__name__)

# URI du replica set
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["shop"]
products_collection = db["items"]

# Redis setup
REDIS_HOST = os.getenv("REDIS_HOST", "redis.dev.svc.cluster.local")  # nom du service Redis dans k8s
REDIS_PORT = 6379
cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@app.route('/')
def home():
    hostname = socket.gethostname()
    cached = cache.get("items")
    if cached:
        products = json.loads(cached)
    else:
        products = list(products_collection.find({}, {"_id": 0}))
        cache.set("items", json.dumps(products), ex=300)  # TTL 5 min
    return render_template('index.html', pod_name=hostname, products=products)

@app.route('/api/items')
def get_products():
    cached = cache.get("items")
    if cached:
        return cached 
    products = list(products_collection.find({}, {"_id": 0}))
    cache.set("items", json.dumps(products), ex=300)  # TTL 5 min
    return jsonify(products)

print("Hello world! Version test:")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
