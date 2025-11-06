from flask import Flask, jsonify
import requests

app = Flask(__name__)

# Coordenadas aproximadas alrededor del AICM
LAT_MIN = 19.0
LAT_MAX = 19.8
LON_MIN = -99.5
LON_MAX = -98.8

@app.route('/vuelos_cdmx', methods=['GET'])
def obtener_vuelos_cdmx():
    url = (
        f"https://opensky-network.org/api/states/all?"
        f"lamin={LAT_MIN}&lomin={LON_MIN}&lamax={LAT_MAX}&lomax={LON_MAX}"
    )
    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        vuelos = []
        if data and "states" in data and data["states"]:
            for estado in data["states"]:
                vuelo = {
                    "icao24": estado[0],
                    "callsign": estado[1].strip() if estado[1] else None,
                    "pais_origen": estado[2],
                    "longitud": estado[5],
                    "latitud": estado[6],
                    "altitud": estado[7],
                    "velocidad": estado[9],
                    "direccion": estado[10],
                    "vertical_rate": estado[11],
                    "squawk": estado[14],
                    "hora_actualizacion": data["time"]
                }
                vuelos.append(vuelo)

        return jsonify({
            "zona": "CDMX",
            "total_vuelos": len(vuelos),
            "vuelos": vuelos
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
