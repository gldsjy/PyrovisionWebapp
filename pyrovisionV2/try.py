# from flask import Flask, jsonify, render_template
# import random
# import threading
# import mysql.connector
# from datetime import datetime
# from drone_functions.detection import fireDetection

# def insertDataToDb(time, intensity):
#     try:
#         conn = mysql.connector.connect(
#             host="localhost",
#             port="3306",
#             user="root", 
#             password="12272004",
#             database="db_pyrovision"
#         )
#         cursor = conn.cursor()
#         query = "INSERT INTO tbl_firelog (Time_Detected, Intensity) VALUES (%s, %s)"
#         values = (time, intensity)
#         cursor.execute(query, values)
#         conn.commit()
#         print(f"Inserted {time}, {intensity}") 
#     except mysql.connector.Error as err:
#         print(f"Database error: {err}")
#     finally:
#         cursor.close()
#         conn.close()


# def getDataFromDrone():
#     prevDetection = False
#     while True:    
#         detected, intensity = fireDetection()
#         if detected:
#             if not prevDetection: 
#                 latest_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                 latest_intensity = intensity
#                 insertDataToDb(latest_time, latest_intensity)
#                 prevDetection = True
#             else:
#                 print("Fire still present — not logging again")
#         else:
#             print("No fire detected")
#             prevDetection = False  # reset when fire goes away

#         threading.Event().wait(5)

# threading.Thread(target=getDataFromDrone, daemon=True).start()

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template('pyroindex.html')

# @app.route('/chart-data')
# def chart_data():
#     try:
#         conn = mysql.connector.connect(
#             host="localhost",
#             port="3306",
#             user="root", 
#             password="12272004",
#             database="db_pyrovision"
#         )
#         cursor = conn.cursor()
#         cursor.execute("SELECT Time_Detected, Intensity FROM tbl_firelog ORDER BY Time_Detected DESC LIMIT 10")
#         rows = cursor.fetchall()
#         rows.reverse()  

#         labels = [row[0].strftime("%H:%M:%S") for row in rows]
#         # Convert intensity values to numeric
#         values = [80 if row[1] == "High" else 20 for row in rows]

#     except mysql.connector.Error as err:
#         print(f"Database error: {err}")
#         labels, values = [], []
#     finally:
#         cursor.close()
#         conn.close()

#     return jsonify({
#         "labels": labels,
#         "values": values
#     })

# @app.route('/alert-message')
# def alert_message():
#     alertType = random.choice(["Fire Detected", "Low water level", "Error"])
#     return jsonify({"message": alertType})

# if __name__ == '__main__':
#     app.run(debug=True, use_reloader=False)
