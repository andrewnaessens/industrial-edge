import os
import time
import json
import ssl
import random  # For mock data
import paho.mqtt.client as mqtt

# Configuration (secrets)
BROKER = os.getenv("MQTT_BROKER", "your-id.s2.eu.hivemq.cloud")
PORT = 8883
USER = os.getenv("MQTT_USER", "your-username")
PASS = os.getenv("MQTT_PASS", "your-password")
TOPIC = "factory/edge/vitals"

# Callbacks (connect/disconnect)
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[CONNECTED] Linked to HiveMQ: {BROKER}")
    else:
        print(f"[FAILED] Connection error code: {rc}")

def on_disconnect(client, userdata, disconnect_flags, rc, properties=None):
    # rc == 0 means the disconnect was from the code (clean)
    if rc == 0:
        print("[OFFLINE] Disconnected cleanly from HiveMQ.")
    else:
        print(f"[OFFLINE] Unexpected connection loss (Error {rc}). Industrial Ege Hub will auto-reconnect...")

# Sensor Logic
def read_vitals():
    # Check if we are on a Pi with I2C enabled
    if os.path.exists("/dev/i2c-1"):
        try:
            # Sensor libraries are imported here so program can run on Laptop with mock data
            from seeed_dht import DHT
            from grove.grove_light_sensor_v1_2 import GroveLightSensor

            # Grove - Light Sensor connected to port A2
            lightSensor = GroveLightSensor(2)
            # Grove - Temperature/Humidity Sensor connected to port D5
            sensor = DHT("11", 5)
            
            # Read temperature/humidity sensor
            humi, temp = sensor.read()
            # Read light sensor
            light = lightSensor.light

            # Sensor Data: Real sensor data from hardware (edge device: raspberry pi)
            return {
                "mode": "hardware", 
                "temperature": f"{temp:.1f}C", 
                "humidity": f"{humi:.1f}%", 
                "illuminance": f"{light:.1f}lx"
            }
        except Exception as e:
            return {"mode": "error", "message": str(e)}
    else:
        # Mock Data: Simulates industrial vitals for testing on laptop
        return {
            "mode": "mock",
            "temperature": round(random.uniform(20.0, 25.0), 2),
            "humidity": round(random.uniform(40.0, 50.0), 2),
            "illuminance": round(random.uniform(300, 500), 1)
        }

# MQTT Setup/Run
def main():
    # Setup Client
    # Use Paho 2.0+ Callback API    
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2)
    client.username_pw_set(USER, PASS)

    # Attach the resilience handlers
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    # Trigger connection in the Background
    print(f"[CONNECTING TO CLOUD] Linking to HiveMQ...")
    try:
        client.connect(BROKER, PORT, keepalive=60)
        # Starting background loop
        # Paho MQTT Library spins up a new, independent thread that handles networking:
        # Manages TLS/SSL encryption
        # Sending "pings" to HiveMQ every 60 seconds so the broker knows the Pi is there
        # Automatically trys to reconnect if the Wi-Fi drops
        client.loop_start()
    except Exception as e:
        print(f"Initial Cloud Handshake failed: {e}. Proceeding in Offline Mode until connection is established.")

    # Start Local Monitoring immediately
    print("Local Monitoring: ACTIVE")
    
    try:    
        while True:
            vitals = read_vitals()
            # If cloud is down, Paho MQTT buffers message
            # QoS 1 ensures HiveMQ acknowledges receipt
            client.publish(TOPIC, json.dumps(vitals), qos=1)
            print(f"[LOG] {vitals}")
            # Wait 5 seconds before next reading
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n Shutting down...")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
