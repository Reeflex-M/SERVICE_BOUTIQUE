from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import paho.mqtt.client as mqtt
import json
import os

app = FastAPI(title="Service d'alarme")

# Configuration MQTT
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

class Alarm(BaseModel):
    id: Optional[int] = None
    message: str
    timestamp: str
    active: bool = True
    type: str = "manual"  # manuel ou security


alarms_list = []
alarm_counter = 1

# Client MQTT
mqtt_client = mqtt.Client()

def on_message(client, userdata, message):
    topic = message.topic
    payload = json.loads(message.payload.decode())
    print(f"📡 MQTT reçu sur {topic}: {payload}")
    
    if topic == "boutique/alarm" and payload["type"] == "security_alarm":
        creer_alarme_auto(payload["message"], "security")

def creer_alarme_auto(message: str, type_alarme: str = "security"):
    """Créer une alarme automatiquement via MQTT"""
    global alarm_counter
    
    nouvelle_alarme = Alarm(
        id=alarm_counter,
        message=message,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        active=True,
        type=type_alarme
    )
    
    alarms_list.append(nouvelle_alarme)
    alarm_counter += 1
    
    print(f"NOUVELLE ALARME AUTO: {message}")
    return nouvelle_alarme

def connect_mqtt():
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    
    mqtt_client.subscribe("boutique/alarm")
    
    mqtt_client.loop_start()
    print(f"MQTT connecté à {MQTT_BROKER}:{MQTT_PORT}")
    print("Écoute des alarmes: boutique/alarm")


connect_mqtt()

@app.get("/")
def accueil():
    return {"message": "Service d'alarme - boutique"}

@app.get("/health")
def health():
    return {"status": "OK", "service": "alarm-simple"}

@app.get("/alarmes", response_model=List[Alarm])
def obtenir_alarmes():
    """Recup toutes les alarmes"""
    return alarms_list

@app.get("/alarmes/actives", response_model=List[Alarm])
def obtenir_alarmes_actives():
    """recup les alarmes actives"""
    return [alarm for alarm in alarms_list if alarm.active]

@app.get("/alarmes/security")
def obtenir_alarmes_security():
    """Récupérer seulement les alarmes de sécurité"""
    return [alarm for alarm in alarms_list if alarm.type == "security"]

@app.post("/alarme", response_model=Alarm)
def creer_alarme(message: str):
    """crée nouvelle alarme manuelle"""
    return creer_alarme_auto(message, "manual")

if __name__ == '__main__':
    import uvicorn
    print("🚀 Service alarme démarré sur le port 8003")
    uvicorn.run(app, host="0.0.0.0", port=8003) 