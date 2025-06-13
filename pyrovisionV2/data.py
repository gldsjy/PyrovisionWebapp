from flask import Flask, jsonify, request, render_template, Response
import mysql.connector
from datetime import datetime
import threading
import requests
import time

app = Flask(__name__)


# =============================
# Replace with your actual MySQL credentials
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "12272004",
    "database": "db_pyrovision"
}
# =============================


# ESP32 Camera and drone base URL
ESP32_BASE_URL = "http://192.168.0.104"  # update this to your ESP32 IP


# Global status flags and data holders
esp32_camera_connected = False
esp32_connected = False
system_powered_on = False
spraying_manual_override = False
fire_being_handled = False
latest_fire_log = None  # To store last fire detection info for suppressing logs


# Lock for thread safety in fire handling loop
fire_lock = threading.Lock()

def db_insert_fire_log(timestamp, intensity):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "INSERT INTO tbl_firelog (Time_Detected, Intensity) VALUES (%s, %s)"
        cursor.execute(query, (timestamp, intensity))
        conn.commit()
        print(f"[DB] Inserted fire log at {timestamp} with intensity {intensity}")
    except mysql.connector.Error as err:
        print(f"[DB ERROR]: {err}")
    finally:
        cursor.close()
        conn.close()


@app.route('/api/status', methods=['GET', 'POST'])
def status():
    global esp32_connected, esp32_camera_connected, system_powered_on, spraying_manual_override, fire_being_handled


    if request.method == 'POST':
        data = request.json or {}


        # Update only if key exists in the payload
        esp32_connected = data.get("esp32_connected", esp32_connected)
        esp32_camera_connected = data.get("esp32_camera_connected", esp32_camera_connected)
        system_powered_on = data.get("system_powered_on", system_powered_on)
        spraying_manual_override = data.get("spraying_manual_override", spraying_manual_override)
        fire_being_handled = data.get("fire_being_handled", fire_being_handled)


        print("[ESP32] Updated Status:")
        print(f"  esp32_connected: {esp32_connected}")
        print(f"  esp32_camera_connected: {esp32_camera_connected}")
        print(f"  system_powered_on: {system_powered_on}")
        print(f"  spraying_manual_override: {spraying_manual_override}")
        print(f"  fire_being_handled: {fire_being_handled}")


        return jsonify({"message": "ESP32 status updated"}), 200


    # For GET requests
    return jsonify({
        "esp32_camera_connected": esp32_camera_connected,
        "esp32_connected": esp32_connected,
        "system_powered_on": system_powered_on,
        "spraying_manual_override": spraying_manual_override,
        "fire_being_handled": fire_being_handled
    })


def check_esp32_devices():
    global esp32_camera_connected, esp32_connected
    # Check ESP32 Camera connection
    try:
        resp = requests.get(f"{ESP32_BASE_URL}/api/camera-status", timeout=3)
        print("resp: ", resp.status_code)
        if resp.status_code == 200:
            esp32_camera_connected = True
            print("ESP32 CAMERA Connected")
    except:
        esp32_camera_connected = False
        print("ESP32 CAMERA Not Connected")

    # Check ESP32 main device connection
    try:
        resp = requests.get(f"{ESP32_BASE_URL}/api/status")
        if resp.status_code == 200:
            esp32_connected = True
            print("ESP32 Connected")
        else:
            print(f"ESP32 responded with status code: {resp.status_code}")
    except Exception as e:
        esp32_connected = False
        print(f"Error connecting to ESP32: {e}")
        print("ESP32 Not Connected")


@app.route('/')
def index():
    # Serve your frontend web app here, serve PyroVision or equivalent HTML page
    # For demo, a simple page with links to status and controls endpoints
    return render_template("pyroindex.html")


# Endpoint to receive fire detection posts from ESP32 camera
@app.route('/api/fire-log', methods=['POST'])
def fire_log():
    global fire_being_handled, latest_fire_log

    data = request.json
    detected = data.get("detected", False)
    width = data.get("width", 0)
    height = data.get("height", 0)


    if detected and not fire_being_handled:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


        intensity = "Low" if (width < 10 and height < 10) else "High"
        latest_fire_log = {
            "timestamp": timestamp,
            "intensity": intensity,
            "width": width,
            "height": height
        }

        fire_being_handled = True
       
        print("Fire Detected")
        print(f"Timestamp: {timestamp}")
        print(f"Intensity: {intensity} Fire Intensity")

        # Log fire detection in DB
        db_insert_fire_log(timestamp, intensity)

        # Inform frontend / webapp as needed (push via websocket or polling)
        # Here, could implement a notification system.
        # Command drone to hover, navigate and extinguish handled by ESP32 itself and reflected by further posts


    elif not detected and fire_being_handled:
        # Fire extinguished condition (e.g. no fire data for some time)
        fire_being_handled = False
        print("Fire Successfully Extinguished")

    return jsonify({"status": "received"})

@app.route('/chart-data')
def chart_data():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            port="3306",
            user="root",
            password="12272004",
            database="db_pyrovision"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT Time_Detected, Intensity FROM tbl_firelog ORDER BY Time_Detected DESC LIMIT 10")
        rows = cursor.fetchall()
        rows.reverse()  

        labels = [row[0].strftime("%H:%M:%S") for row in rows]
        values = [80 if row[1] == "High" else 20 for row in rows]

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        labels, values = [], []
    finally:
        cursor.close()
        conn.close()

    return jsonify({
        "labels": labels,
        "values": values
    })

# Control commands from webapp - Power ON/OFF and Spray ON/OFF
@app.route('/power-status', methods=['GET'])
def power_status():
    return jsonify({"power_on": system_powered_on})


@app.route('/api/control/power', methods=['POST'])
@app.route('/control-power', methods=['POST'])
def control_power():
    global system_powered_on, fire_being_handled

    data = request.json
    command = data.get("command", "")

    if command == "POWER_ON":
        if not system_powered_on:
            system_powered_on = True
            fire_being_handled = False


            print("Power System ON")
            try:
                requests.post(f"{ESP32_BASE_URL}/api/control", json={"command": "POWER_ON"})  
                print("Command sent to ESP32: Searching for Fire")
            except Exception as e:
                print(f"Failed to send POWER_ON command to ESP32: {e}")


            return jsonify({"message": "Power System ON command sent"}), 200
        else:
            print("System already ON. Skipping redundant command.")
            return jsonify({"message": "System already ON"}), 200

    elif command == "POWER_OFF":
        system_powered_on = False


        print("Power System Off / Initiating Landing")
        try:
            requests.post(f"{ESP32_BASE_URL}/api/control", json={"command": "POWER_OFF"})
            print("Command sent to ESP32: Initiating Landing")
        except Exception as e:
            print(f"Failed to send POWER_OFF command to ESP32: {e}")

        return jsonify({"message": "Power System OFF command sent"}), 200

    return jsonify({"error": "Invalid power command"}), 400



@app.route('/spray-manual-status', methods=['GET'])
def spray_status():
    return jsonify({"spray_on": spraying_manual_override})



@app.route('/api/control/spray', methods=['POST'])
@app.route('/control-spray', methods=['POST'])
def control_spray():
    print("control_spray endpoint called")
    global spraying_manual_override
    data = request.json
    command = data.get("command", "")
    print(f"Received command: {command}")

    if command == "SPRAY_ON":
        spraying_manual_override = True
        print("Manual Spraying ON triggered")
        try:
            requests.post(f"{ESP32_BASE_URL}/api/control", json={"command": "SPRAY_ON"})
            print("Command sent to ESP32: Spray ON")
        except Exception as e:
            print(f"Failed to send SPRAY_ON command to ESP32: {e}")
        return jsonify({"message": "Spraying ON command sent"}), 200


    elif command == "SPRAY_OFF":
        spraying_manual_override = False
        print("Manual Spraying OFF triggered")
        try:
            requests.post(f"{ESP32_BASE_URL}/api/control", json={"command": "SPRAY_OFF"})
            print("Command sent to ESP32: Spray OFF")
        except Exception as e:
            print(f"Failed to send SPRAY_OFF command to ESP32: {e}")
        return jsonify({"message": "Spraying OFF command sent"}), 200


    return jsonify({"error": "Invalid spray command"}), 400



def periodic_status_check():
    while True:
        check_esp32_devices()
        time.sleep(10)  # Check every 10 seconds

if __name__ == '__main__':
    # Start background thread for periodic connection check
    threading.Thread(target=periodic_status_check, daemon=True).start()

    # Print the webapp url on startup
    print("Flask server running at: http://0.0.0.0:5000")
    print("Checking ESP32 connections...")
    check_esp32_devices()

    app.run(host='0.0.0.0', port=5000, debug=True)



