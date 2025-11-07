import mysql.connector
from werkzeug.security import generate_password_hash
import sys

# --- Configuración de la base de datos ---
# (Asegúrate de que coincida con tu app.py)
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "admin123", # Tu contraseña de DB
    "database": "monitorvuelosCDMX"
}

# --- DATOS DEL ADMIN QUE QUIERES CREAR ---
ADMIN_USER = "Angello" # <-- El usuario que escribirás en el formulario
ADMIN_PASS = "admin" # <-- La contraseña que escribirás

try:
    print(f"Conectando a la base de datos '{db_config['database']}'...")
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Encriptar (hashear) la contraseña
    hashed_password = generate_password_hash(ADMIN_PASS)
    
    print(f"Creando usuario '{ADMIN_USER}'...")
    sql_insert = "INSERT INTO usuarios (username, password_hash) VALUES (%s, %s)"
    cursor.execute(sql_insert, (ADMIN_USER, hashed_password))
    
    conn.commit()
    print(f"✅ ¡Éxito! Usuario '{ADMIN_USER}' creado en la base de datos.")
    print("Recuerda borrar o cambiar la contraseña en este script.")

except mysql.connector.Error as err:
    if err.errno == 1062: # Error de 'Duplicate entry'
        print(f"⚠️  Error: El usuario '{ADMIN_USER}' ya existe.")
    else:
        print(f"❌ Error de base de datos: {err}")
    sys.exit(1) # Salir con código de error
finally:
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'conn' in locals() and conn.is_connected():
        conn.close()