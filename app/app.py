from flask import Flask, render_template, jsonify
import socket
import os
import json
from pymongo import MongoClient
import redis  # ← on importe redis

app = Flask(__name__)

# URI du replica set
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["store"]
products_collection = db["products"]

# Redis setup
REDIS_HOST = os.getenv("REDIS_HOST", "redis.dev.svc.cluster.local")  # nom du service Redis dans k8s
REDIS_PORT = 6379
cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@app.route('/')
def home():
    hostname = socket.gethostname()
    # on récupère la liste des produits depuis Redis si elle existe
    cached = cache.get("products")
    if cached:
        products = json.loads(cached)
        print("⚡️ Produits depuis Redis cache")
    else:
        products = list(products_collection.find({}, {"_id": 0}))
        cache.set("products", json.dumps(products), ex=300)  # TTL 5 min
        print("💾 Produits mis en cache dans Redis")
    return render_template('index.html', pod_name=hostname, products=products)

@app.route('/api/products')
def get_products():
    cached = cache.get("products")
    if cached:
        print("⚡️ Returning products from Redis cache")
        return cached  # JSON string
    products = list(products_collection.find({}, {"_id": 0}))
    cache.set("products", json.dumps(products), ex=300)  # TTL 5 min
    print("💾 Products cached in Redis")
    return jsonify(products)

print("Hello world! Version test:")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
