from flask import Flask, render_template, jsonify
import socket

app = Flask(__name__)

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
    return jsonify(products)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
