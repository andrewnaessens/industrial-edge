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
            from grove.grove_led import GroveLed

            # Grove - Temperature/Humidity Sensor connected to port D5
            temp_humi_sensor = DHT("11", 5)
            # Grove - Light Sensor connected to port A2
            light_sensor = GroveLightSensor(2)
            # Grove - LED connected to port D22
            led1 = GroveLed(22)
            # Grove - LED connected to port D24
            led2 = GroveLed(24)
            # Grove - LED connected to port D26
            led3 = GroveLed(26)

            # Read temperature/humidity sensor
            humi, temp = temp_humi_sensor.read()
             # Read light sensor
            light = light_sensor.light
            
            # Temperature thresholds
            temp_thresh1 = 5.0
            temp_thresh2 = 25.0
            # Humidity threshold
            humi_thresh1 = 60
            # Light threshold
            light_thresh1 = 200

            # If temperature sensor reading is less than/equal to temperature threshold1
            # and less than/equal to temperature threshold2 "Within safe temperature range!"
            # else "Outside safe temperature range!"
            if temp_thresh1 <= temp and temp <= temp_thresh2:
                temp_event = "Within safe temperature range!"
                led1.off()
            else:
                temp_event = "Outside safe temperature range!"
                led1.on()

            # If humidity sensor reading is less than/equal to humidity threshold 
            # "Within safe humidity range!" else "Outside safe humidity range!"
            if humi <= humi_thresh1:
                humi_event = "Within safe humidity range!"
                led2.off()
            else: 
                humi_event = "Outside safe humidity range!"
                led2.on()

            # If light sensor reading is greater than/equal to light threshold 
            # "Enought light!" else "Not enough light!"
            if light >= light_thresh1:
                illuminance_event = "Sufficient light!"
                led3.off()
            else: 
                illuminance_event = "Insufficient light!"
                led3.on()

            # Sensor Data: Real sensor data from hardware (edge device: raspberry pi)
            return {
                "mode": "hardware", 
                "temperature": f"{temp:.1f}", 
                "temperature_event": f"{temp_event}",
                "humidity": f"{humi:.1f}",
                "humidity_event": f"{humi_event}",
                "illuminance": f"{light:.1f}",
                "illuminance_event": f"{illuminance_event}"
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
