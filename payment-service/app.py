from fastapi import FastAPI
import paho.mqtt.client as mqtt
import json
import os

app = FastAPI(title="Paiement Simple")

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

paiements = []
compteur_id = 1

@app.get("/")
def accueil():
    return {"message": "Service Paiement Simple"}

@app.get("/paiements")
def voir_paiements():
    return paiements

@app.post("/payer")
def payer(produit: str, montant: float):
    global compteur_id
    
    nouveau_paiement = {
        "id": compteur_id,
        "produit": produit,
        "montant": montant,
        "statut": "payé"
    }
    
    paiements.append(nouveau_paiement)
    compteur_id += 1
    
    print(f"Paiement reçu: {montant}€ pour {produit}")
    
    # Publier sur MQTT
    message = {
        "type": "payment_success",
        "produit": produit,
        "montant": montant,
        "id": nouveau_paiement["id"]
    }
    mqtt_client.publish("boutique/payment", json.dumps(message))
    print(f"📡 MQTT publié: paiement réussi pour {produit}")
    
    return {"message": "Paiement réussi", "id": nouveau_paiement["id"]}

if __name__ == '__main__':
    import uvicorn
    print("🚀 Paiement Simple sur port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000) 