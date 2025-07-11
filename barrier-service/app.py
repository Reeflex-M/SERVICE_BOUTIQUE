from fastapi import FastAPI
import paho.mqtt.client as mqtt
import json
import os
import threading
import time

app = FastAPI(title="Barrière Simple")

# Configuration MQTT
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

# true -> ouvert, false -> fermé
barriere_ouverte = False

produits_pris = {}  
produits_payes = {}  

# Client MQTT
mqtt_client = mqtt.Client()

def on_message(client, userdata, message):
    topic = message.topic
    payload = json.loads(message.payload.decode())
    print(f"📡 MQTT reçu sur {topic}: {payload}")
    
    if topic == "boutique/product" and payload["type"] == "product_taken":
        # Produit pris
        produit_id = payload["produit_id"]
        produits_pris[produit_id] = {
            "nom": payload["produit_nom"],
            "pris_timestamp": time.time()
        }
        print(f"🛒 Produit pris: {payload['produit_nom']} (ID: {produit_id})")
        
        # Timer pour vérifier le paiement (10 secondes)
        threading.Timer(10.0, verifier_paiement, [produit_id]).start()
        
    elif topic == "boutique/payment" and payload["type"] == "payment_success":
        # Paiement réussi
        produit_nom = payload["produit"]
        # Trouver le produit par nom
        for pid, info in produits_pris.items():
            if info["nom"].lower() in produit_nom.lower():
                produits_payes[pid] = True
                print(f"Paiement confirmé pour: {produit_nom}")
                ouvrir_barriere_auto()
                break

def verifier_paiement(produit_id):
    """Vérifier si un produit pris a été payé après 10 secondes"""
    if produit_id not in produits_payes:
        # produit pas payé
        produit_info = produits_pris.get(produit_id, {})
        print(f"ALARME: Produit non payé - {produit_info.get('nom', f'ID:{produit_id}')}")
        
        # Publier alarme via MQTT
        alarme_msg = {
            "type": "security_alarm",
            "message": f"Produit non payé: {produit_info.get('nom', f'ID:{produit_id}')}",
            "produit_id": produit_id
        }
        mqtt_client.publish("boutique/alarm", json.dumps(alarme_msg))
        print("📡 Alarme envoyée via MQTT")

def ouvrir_barriere_auto():
    """Ouvrir automatiquement la barrière après paiement"""
    global barriere_ouverte
    barriere_ouverte = True
    print("🚪 Barrière OUVERTE automatiquement (paiement confirmé)")
    
    # Auto-fermeture après 5 secondes
    threading.Timer(5.0, fermer_barriere_auto).start()

def fermer_barriere_auto():
    """Fermer automatiquement la barrière"""
    global barriere_ouverte
    barriere_ouverte = False
    print("🚪 Barrière FERMÉE automatiquement")

def connect_mqtt():
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    
    # S'abonner aux topics
    mqtt_client.subscribe("boutique/product")
    mqtt_client.subscribe("boutique/payment")
    
    mqtt_client.loop_start()
    print(f"MQTT connecté à {MQTT_BROKER}:{MQTT_PORT}")
    print("Écoute des messages: boutique/product et boutique/payment")

# Connexion MQTT au démarrage
connect_mqtt()

@app.get("/")
def accueil():
    return {"message": "Service barriere"}

@app.get("/status")
def status():
    return {
        "barriere": "ouverte" if barriere_ouverte else "fermée",
        "produits_pris": len(produits_pris),
        "produits_payes": len(produits_payes)
    }

@app.post("/ouvrir")
def ouvrir():
    global barriere_ouverte
    barriere_ouverte = True
    print("Barrière OUVERTE (manuel)")
    return {"message": "Barrière ouverte"}

@app.post("/fermer")
def fermer():
    global barriere_ouverte
    barriere_ouverte = False
    print("Barrière FERMÉE (manuel)")
    return {"message": "Barrière fermée"}

if __name__ == '__main__':
    import uvicorn
    print("🚀 Barrière Simple sur port 8002")
    uvicorn.run(app, host="0.0.0.0", port=8002) 