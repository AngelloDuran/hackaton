#!/bin/bash

# Configuración de MySQL
DB_HOST="127.0.0.1"
DB_USER="root"
DB_PASS="admin123"
DB_NAME="monitorvuelosCDMX"

# Configuración de Zabbix
ZABBIX_SERVER="98.12.20.26"
ZABBIX_PORT=10051
HOSTNAME="MiUbuntuAgent"

# Consulta SQL para obtener los vuelos
mysql -h $DB_HOST -u $DB_USER -p$DB_PASS -D $DB_NAME -e "
SELECT id_vuelo, velocidad, altitud, distancia_a_cdmx FROM vuelo;
" -N | while read id vuelo_vel vuelo_alt vuelo_dist; do
    # Envía cada campo como métrica
    zabbix_sender -z $ZABBIX_SERVER -p $ZABBIX_PORT -s $HOSTNAME -k "vuelo.velocidad[$id]" -o $vuelo_vel
    zabbix_sender -z $ZABBIX_SERVER -p $ZABBIX_PORT -s $HOSTNAME -k "vuelo.altitud[$id]" -o $vuelo_alt
    zabbix_sender -z $ZABBIX_SERVER -p $ZABBIX_PORT -s $HOSTNAME -k "vuelo.distancia_a_cdmx[$id]" -o $vuelo_dist
done
