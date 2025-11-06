from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)  # ✅ Solo una vez

# 🔧 CONFIGURACIÓN DE LA BASE DE DATOS
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "admin123",
    "database": "monitorvuelosCDMX"
}

# 🔭 Coordenadas de CDMX
CDMX_COORDS = {"lat": 19.4361, "lon": -99.0719}
RANGO = 2.5  # grados (~275 km)

@app.route("/api/vuelos")  
def obtener_vuelos():
    url = f"https://opensky-network.org/api/states/all?lamin={CDMX_COORDS['lat'] - RANGO}&lomin={CDMX_COORDS['lon'] - RANGO}&lamax={CDMX_COORDS['lat'] + RANGO}&lomax={CDMX_COORDS['lon'] + RANGO}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if not data.get("states"):
            return jsonify({"mensaje": "No hay datos de vuelos disponibles."}), 404

        vuelos = []
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        for vuelo in data["states"]:
            callsign = vuelo[1] or "Sin ID"
            lon = vuelo[5]
            lat = vuelo[6]
            altitud = vuelo[7] or 0
            velocidad = vuelo[9] or 0
            hora_actualizacion = datetime.utcfromtimestamp(data["time"]).strftime('%Y-%m-%d %H:%M:%S')

            if not lat or not lon:
                continue

            # Insertar o actualizar en MySQL
            query = """
                INSERT INTO vuelo (callsign, latitud, longitud, altitud, velocidad, hora_actualizacion, es_llegada_cdmx)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    latitud = VALUES(latitud),
                    longitud = VALUES(longitud),
                    altitud = VALUES(altitud),
                    velocidad = VALUES(velocidad),
                    hora_actualizacion = VALUES(hora_actualizacion);
            """
            cursor.execute(query, (callsign, lat, lon, altitud, velocidad, hora_actualizacion, True))

            vuelos.append({
                "callsign": callsign,
                "latitud": lat,
                "longitud": lon,
                "altitud": altitud,
                "velocidad": velocidad
            })

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"vuelos": vuelos})  

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return "🌎 API de Monitoreo de Vuelos CDMX activa 🚀"


if __name__ == "__main__":
    app.run(debug=True)
