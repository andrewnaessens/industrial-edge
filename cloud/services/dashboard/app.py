import os
from datetime import datetime
import json
import threading
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

# Load local .env from the dashboard folder
load_dotenv()

app = Flask(__name__)

# Global variable to store the latest Pi sensor data
vitals = {
    "temperature": "--",
    "temperature_event": "--",
    "humidity": "--", 
    "humidity_event": "--",
    "illuminance": "--", 
    "illuminance_event": "--",
    "status": "Offline",
    "last_seen": "Never"
}

# Callbacks (connect/message) for HiveMQ Cloud
def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("Dashboard connected to HiveMQ Cloud!")
        client.subscribe("factory/edge/vitals")
    else:
        print(f"Connection failed: {rc}")

def on_message(client, userdata, msg):
    # Use the global vitals variable
    global vitals
    try:
        # msg.payload is a byte-string (b'{"temp": 22...}')
        # .decode() turns it into a Python string
        payload = msg.payload.decode()
        # Parse the JSON
        data = json.loads(payload)
        # Update the vitals variable
        vitals.update(data)
        vitals["status"] = "Online"
        vitals["last_seen"] = datetime.now().strftime("%H:%M:%S")
        # Log the update (print to the console)
        print(f"Live Cloud Update: {vitals['last_seen']} Vitals: {vitals}")
    except Exception as e:
        # Log the error (print to the console)
        print(f"Parsing error: {e}")

# Background thread for MQTT
def start_mqtt():
    # Use VERSION2 for Paho 2.1.0+
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(os.environ.get("MQTT_USER"), os.environ.get("MQTT_PASSWORD"))
    client.tls_set() # Required for HiveMQ Cloud SSL
    
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect(os.environ.get("MQTT_BROKER"), 8883, 60)
    client.loop_start()

start_mqtt()

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    return jsonify(vitals)

if __name__ == '__main__':
    app.run(debug=True)
