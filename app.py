from dotenv import load_dotenv
from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import os

# load_dotenv() # Use when doing local dev

MQTT_BROKER = os.environ.get("MQTT_BROKER")
MQTT_PORT = int(os.environ.get("MQTT_PORT"))
MQTT_TOPIC = os.environ.get("MQTT_TOPIC")
MQTT_USERNAME= os.environ.get("MQTT_USERNAME")
MQTT_PASSWORD= os.environ.get("MQTT_PASSWORD")

app = Flask(__name__)

def on_cloud_connect(client, userdata, flags, rc):
    print("[MQTT] Connected with result code", rc)

def on_cloud_message(client, userdata, msg):
    print("[MQTT] Received:", msg.topic, msg.payload.decode())

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
mqtt_client.tls_set()
mqtt_client.on_connect = on_cloud_connect
mqtt_client.on_message = on_cloud_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

@app.route('/broadcast', methods=['POST'])
def broadcast_message():
    data = request.get_json()
    payload = {}
    message = data.get("message", "")

    # We are turning on or turning off the system
    if "systemState" in data:
        payload["systemState"] = data.get("systemState", "")

    # At this point one of the bowls needs to be filled, we need the other bowl's info to give a complete message, if we have both then the water bowl will just send it, it may not look obvious but this just works
    if "notifWater" in data or "notifFood" in data:
        payload.update(data)

    if "requestFoodData" in data:
        payload["requestFoodData"] = "true"

    if "requestedFood" in data:
        payload.update(data)

    mqtt_client.publish(MQTT_TOPIC, str(payload).replace("'", '"'))
    return jsonify({"status": "broadcasted", "message": message})

@app.route('/')
def index():
    return "MQTT Broadcast API is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
