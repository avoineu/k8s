import sys
import os
import pytest
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_mongo():
    """Mock des produits MongoDB"""
    products = [
        {"name": "Laptop", "price": 1200},
        {"name": "T-shirt Kubernetes", "price": 25},
    ]
    with patch("app.products_collection") as mock_collection:
        mock_collection.find.return_value = products
        yield mock_collection

@pytest.fixture
def mock_redis():
    """Mock Redis pour que le test ne tente pas de se connecter à Redis réel"""
    with patch("app.cache") as mock_cache:
        # Simule que le cache est vide
        mock_cache.get.return_value = None
        # Simule set() sans erreur
        mock_cache.set.return_value = True
        yield mock_cache

def test_api_products_status(client, mock_mongo, mock_redis):
    """Teste que l'API /api/items renvoie bien les produits"""
    response = client.get("/api/items")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(p["name"] == "Laptop" for p in data)
    assert all("name" in p and "price" in p for p in data)