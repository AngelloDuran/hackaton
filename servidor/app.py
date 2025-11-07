from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import requests
import traceback
from datetime import datetime
import threading
import time
from werkzeug.security import check_password_hash
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)


app = Flask(__name__)
# --- Configuración para Login ---
# ¡MUY IMPORTANTE! Flask necesita esto para encriptar la cookie de sesión
app.config["SECRET_KEY"] = "ea5293fff1b5f26fc0b782d72e5267731e0b074b0eec2bd7"
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"success": False, "message": "Rellena todos los campos"}), 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        user_data = cursor.fetchone()

        if not user_data:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

        # Verificar contraseña
        if not check_password_hash(user_data["password_hash"], password):
            return jsonify({"success": False, "message": "Contraseña incorrecta"}), 401

        # Crear objeto User y hacer login
        user = User(user_data["id_user"], user_data["username"], user_data["password_hash"])
        login_user(user)  # Flask-Login crea la sesión y cookie
        return jsonify({"success": True, "message": "Login exitoso"})
    except Exception as e:
        print("❌ ERROR en /api/login:", e)
        return jsonify({"success": False, "message": "Error en el servidor"}), 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "conn" in locals() and conn.is_connected():
            conn.close()

# Configurar CORS para permitir credenciales (cookies) desde tu app de React
CORS(
    app,
    resources={r"/api/*": {"origins": ["http://localhost:5173", "http://localhost:3000"]}},
    supports_credentials=True,
)

# 🔧 Configuración de la base de datos
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "admin123",
    "database": "monitorvuelosCDMX"
}

# 🔭 Coordenadas de CDMX
CDMX_COORDS = {"lat": 19.4361, "lon": -99.0719}
RANGO = 2.5  # grados (~275 km)

# 🔐 Tus credenciales de OpenSky API (OAuth2)
CLIENT_ID = "angello-api-client"
CLIENT_SECRET = "TWHO2sSgzeXtpRx7798xbAAUXJQDdEf3"

ACCESS_TOKEN = None
TOKEN_EXPIRA = 0


# --- Configuración de Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)

# Clase de Usuario que Flask-Login usará
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    """Carga un usuario desde la BD para la sesión."""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM administrador WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        
        if user_data:
            return User(
                user_data["id"], user_data["username"], user_data["password_hash"]
            )
        return None
    except mysql.connector.Error as err:
        print(f"Error de DB al cargar usuario: {err}")
        return None
    finally:
        if "cursor" in locals():
            cursor.close()
        if "conn" in locals() and conn.is_connected():
            conn.close()

# --- Funciones de OpenSky (Tu código) ---

# 🔑 Función para obtener el token de acceso
def obtener_token():
    global ACCESS_TOKEN, TOKEN_EXPIRA
    try:
        url_token = "https://opensky-network.org/oauth/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }

        print("🔑 Solicitando token de acceso a OpenSky...")
        r = requests.post(url_token, data=data)
        r.raise_for_status()
        token_data = r.json()
        ACCESS_TOKEN = token_data.get("access_token")
        TOKEN_EXPIRA = time.time() + token_data.get("expires_in", 3600)
        print("✅ Token obtenido correctamente.")
    except Exception as e:
        print("❌ Error al obtener token:")
        print(traceback.format_exc())


# 🕒 Función que consulta OpenSky y guarda en MySQL
def actualizar_vuelos():
    global ACCESS_TOKEN, TOKEN_EXPIRA

    while True:
        try:
            # 🔁 Si el token expiró o no existe, obtener uno nuevo
            if not ACCESS_TOKEN or time.time() >= TOKEN_EXPIRA:
                obtener_token()
                if not ACCESS_TOKEN:
                    print("❌ No se pudo obtener token, reintentando en 1 hora...")
                    time.sleep(3600)
                    continue

            print("🔄 Actualizando datos de vuelos...")
            url = (
                f"https://opensky-network.org/api/states/all"
                f"?lamin={CDMX_COORDS['lat'] - RANGO}"
                f"&lomin={CDMX_COORDS['lon'] - RANGO}"
                f"&lamax={CDMX_COORDS['lat'] + RANGO}"
                f"&lomax={CDMX_COORDS['lon'] + RANGO}"
            )

            headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()

            if not data.get("states"):
                print("⚠️ No se recibieron datos de vuelos.")
                time.sleep(3600)
                continue

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

            conn.commit()
            cursor.close()
            conn.close()

            print("✅ Datos actualizados correctamente.")

        except Exception as e:
            print("❌ Error al actualizar vuelos:")
            print(traceback.format_exc())

        # 🕐 Espera 1 hora antes de volver a consultar
        time.sleep(3600)


# 📊 Obtener los últimos vuelos guardados desde la BD
def obtener_datos_vuelos():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT callsign, latitud, longitud, altitud, velocidad, hora_actualizacion
            FROM vuelo
            ORDER BY hora_actualizacion DESC
            LIMIT 50
        """)
        vuelos = cursor.fetchall()

        cursor.close()
        conn.close()

        return vuelos
    except Exception as e:
        print("❌ Error al leer base de datos:")
        print(traceback.format_exc())
        return []


# 📡 Ruta para consultar los últimos vuelos
@app.route("/api/vuelos", methods=["GET"])
def obtener_vuelos():
    try:
        vuelos = obtener_datos_vuelos()
        return jsonify({"vuelos": vuelos})
    except Exception as e:
        print("❌ ERROR en /api/vuelos:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return "🌎 API de Monitoreo de Vuelos CDMX activa 🚀"


if __name__ == "__main__":
    # 🚀 Ejecutar la actualización automática en un hilo en segundo plano
    hilo_actualizacion = threading.Thread(target=actualizar_vuelos, daemon=True)
    hilo_actualizacion.start()

    app.run(debug=True)
