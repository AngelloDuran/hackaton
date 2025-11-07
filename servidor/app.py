from flask import Flask, jsonify, request
# Asegúrate de que CORS esté configurado para credenciales
from flask_cors import CORS
import mysql.connector
import requests
import traceback
from datetime import datetime
import threading
import time

# --- Nuevas importaciones para Login ---
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
app.config["SECRET_KEY"] = "un-secreto-muy-dificil-de-adivinar"

# Configurar CORS para permitir credenciales (cookies) desde tu app de React
CORS(
    app,
    resources={r"/api/*": {"origins": "http://localhost:3000"}},
    supports_credentials=True,
)


# 🔧 Configuración de la base de datos
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "admin123",
    "database": "monitorvuelosCDMX",
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
            "client_secret": CLIENT_SECRET,
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
        ACCESS_TOKEN = None # Forzar re-intento


# 🕒 Función que consulta OpenSky y guarda en MySQL (MODIFICADA)
def actualizar_vuelos():
    global ACCESS_TOKEN, TOKEN_EXPIRA

    while True:
        try:
            # 🔁 Si el token expiró o no existe, obtener uno nuevo
            if not ACCESS_TOKEN or time.time() >= TOKEN_EXPIRA:
                obtener_token()
                if not ACCESS_TOKEN:
                    print("❌ No se pudo obtener token, reintentando en 60 seg...")
                    time.sleep(60) # Esperar 1 minuto si falla el token
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
                print("⚠️ No se recibieron datos de vuelos (API vacía).")
                time.sleep(30) # Esperar 30 seg y reintentar
                continue

            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # --- Lógica de Actualización MEJORADA ---
            # 1. Vaciar la tabla para tener una foto limpia de los vuelos activos
            cursor.execute("TRUNCATE TABLE vuelo")

            vuelos_para_insertar = []
            hora_actualizacion = datetime.utcfromtimestamp(data["time"]).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            for vuelo in data["states"]:
                callsign = (vuelo[1] or "Sin ID").strip()
                lon = vuelo[5]
                lat = vuelo[6]
                altitud = vuelo[7] or 0
                velocidad = vuelo[9] or 0

                # Solo insertar si tenemos coordenadas
                if lat and lon:
                    vuelos_para_insertar.append(
                        (callsign, lat, lon, altitud, velocidad, hora_actualizacion, True) # True para es_llegada_cdmx
                    )
            
            # 2. Insertar todos los vuelos activos en un solo batch
            if vuelos_para_insertar:
                query = """
                    INSERT INTO vuelo (callsign, latitud, longitud, altitud, velocidad, hora_actualizacion, es_llegada_cdmx)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.executemany(query, vuelos_para_insertar)
                print(f"✅ {cursor.rowcount} vuelos insertados/actualizados.")
            else:
                 print("⚠️ No se encontraron vuelos activos en el área.")

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            print("❌ Error al actualizar vuelos:")
            print(traceback.format_exc())
            # Si el token es inválido (ej. 401), forzar renovación
            if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 401:
                print("Token inválido, forzando renovación...")
                ACCESS_TOKEN = None
        
        # 🕐 Espera 30 segundos antes de volver a consultar (en lugar de 1 hora)
        print("...esperando 30 segundos para próxima actualización...")
        time.sleep(30)


# 📊 Obtener los últimos vuelos guardados desde la BD (MODIFICADA)
def obtener_datos_vuelos():
    """Obtiene TODOS los vuelos activos de la tabla."""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Simplificado: Como la tabla solo tiene vuelos activos, solo los leemos
        cursor.execute("""
            SELECT callsign, latitud, longitud, altitud, velocidad, hora_actualizacion
            FROM vuelo
        """)
        vuelos = cursor.fetchall()

        cursor.close()
        conn.close()

        return vuelos
    except Exception as e:
        print("❌ Error al leer base de datos:")
        print(traceback.format_exc())
        return []


# --- Endpoints de API ---

@app.route("/")
def home():
    return "🌎 API de Monitoreo de Vuelos CDMX activa 🚀"

# --- Endpoints de Autenticación (Añadidos) ---

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM administrador WHERE username = %s", (username,))
        user_data = cursor.fetchone()

        if user_data and check_password_hash(user_data["password_hash"], password):
            # Contraseña correcta. Creamos el usuario y lo logueamos
            user = User(
                user_data["id"], user_data["username"], user_data["password_hash"]
            )
            login_user(user)  # Esto crea la cookie de sesión
            return jsonify({"success": True, "message": "Login exitoso"})
        else:
            # Credenciales incorrectas
            return (
                jsonify({"success": False, "message": "Usuario o contraseña incorrectos"}),
                401,
            )
    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"Error de DB: {err}"}), 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "conn" in locals() and conn.is_connected():
            conn.close()

@app.route("/api/logout", methods=["POST"])
@login_required  # Solo un usuario logueado puede desloguearse
def logout():
    logout_user()  # Esto borra la cookie de sesión
    return jsonify({"success": True, "message": "Logout exitoso"})


@app.route("/api/check_session", methods=["GET"])
def check_session():
    """Endpoint para que React sepa si ya hay una sesión activa al cargar."""
    if current_user.is_authenticated:
        return jsonify({"logged_in": True, "username": current_user.username})
    else:
        return jsonify({"logged_in": False})


# 📡 Ruta para consultar los últimos vuelos (¡AHORA PROTEGIDA!)
@app.route("/api/vuelos", methods=["GET"])
@login_required # <-- ¡AÑADIDO! Solo usuarios logueados pueden ver esto
def obtener_vuelos():
    try:
        vuelos = obtener_datos_vuelos()
        
        # Basado en tu screenshot (image_156d3b.png), tu frontend espera stats
        stats = {
            "hosts_monitoreados": 12, # Valor de ejemplo de tu foto
            "problemas_activos": 3,  # Valor de ejemplo de tu foto
            "carga_promedio_zabbix": 0.75, # Valor de ejemplo de tu foto
            "vuelos_activos": len(vuelos), # ¡Este es el dato real!
            "alerta_vuelo_zabbix": 2, # Valor de ejemplo de tu foto
            "latencia_api_ms": 55 # Valor de ejemplo de tu foto
        }

        # Devolver ambos, los vuelos para el mapa y los stats para el dashboard
        return jsonify({"vuelos": vuelos, "stats": stats})
    
    except Exception as e:
        print("❌ ERROR en /api/vuelos:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # 🚀 Ejecutar la actualización automática en un hilo en segundo plano
    print("Iniciando hilo de actualización de vuelos...")
    hilo_actualizacion = threading.Thread(target=actualizar_vuelos, daemon=True)
    hilo_actualizacion.start()

    # 🚀 Iniciar el servidor Flask
    print("Iniciando servidor web en http://localhost:5000 ...")
    app.run(debug=True, port=5000)