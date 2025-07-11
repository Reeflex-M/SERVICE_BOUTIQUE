from fastapi import FastAPI
from pydantic import BaseModel
import paho.mqtt.client as mqtt
import json
import os

app = FastAPI()

# Configuration MQTT
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

# Client MQTT
mqtt_client = mqtt.Client()

def connect_mqtt():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
    print(f"MQTT connecté à {MQTT_BROKER}:{MQTT_PORT}")

# Connexion MQTT au démarrage
connect_mqtt()

class Product(BaseModel):
    id: int = None
    name: str
    price: float
    stock: int

products = [
    {"id": 1, "name": "Café", "price": 2.50, "stock": 10},
    {"id": 2, "name": "Croissant", "price": 1.50, "stock": 5},
    {"id": 3, "name": "Sandwich", "price": 4.00, "stock": 3}
]

@app.get("/products")
def get_products():
    return products

@app.get("/product/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            print(f"🛒 Produit consulté: {product['name']}")
            
            # Publier sur MQTT (produit "pris")
            message = {
                "type": "product_taken",
                "produit_id": product_id,
                "produit_nom": product['name'],
                "prix": product['price']
            }
            mqtt_client.publish("boutique/product", json.dumps(message))
            print(f"MQTT publié: produit pris {product['name']}")
            
            return product
    return None

@app.post("/products")
def create_product(product: Product):
    product.id = len(products) + 1
    products.append(product.dict())
    return product

@app.put("/product/{product_id}")
def update_product(product_id: int, product: Product):
    for i, p in enumerate(products):
        if p['id'] == product_id:
            product.id = product_id
            products[i] = product.dict()
            return product
    return None

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 