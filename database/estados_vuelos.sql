CREATE DATABASE monitorvuelosCDMX;
USE monitorvuelosCDMX;

create table usuarios(
id_user int auto_increment primary key,
username varchar (50),
password_hash varchar(255)
);


-- 1. TABLA PAIS (CORREGIDA)
CREATE TABLE pais (
    id_pais INT AUTO_INCREMENT PRIMARY KEY,
    nombre_pais VARCHAR(100) NOT NULL,
    codigo_iso VARCHAR(3) UNIQUE,
    codigo_alpha2 VARCHAR(2),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABLA AEROPUERTO (CORREGIDA)
CREATE TABLE aeropuerto (
    id_aeropuerto INT AUTO_INCREMENT PRIMARY KEY,
    codigo_icao VARCHAR(4) UNIQUE NOT NULL,
    codigo_iata VARCHAR(3),
    nombre_aeropuerto VARCHAR(150) NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    id_pais INT NOT NULL,
    es_cdmx BOOLEAN DEFAULT FALSE,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_pais) REFERENCES pais(id_pais)
);

-- 3. TABLA ORIGEN (CORREGIDA)
CREATE TABLE origen (
    id_origen INT AUTO_INCREMENT PRIMARY KEY,
    id_pais INT NOT NULL,
    codigo_ciudad VARCHAR(10),
    nombre_ciudad VARCHAR(100),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_pais) REFERENCES pais(id_pais)
);

-- 4. TABLA ESTADO (CORREGIDA)
CREATE TABLE estado (
    id_estado INT AUTO_INCREMENT PRIMARY KEY,
    nombre_estado VARCHAR(50) NOT NULL,
    descripcion VARCHAR(100),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. TABLA RUTA (CORREGIDA)
CREATE TABLE ruta (
    id_ruta INT AUTO_INCREMENT PRIMARY KEY,
    codigo_ruta VARCHAR(10) NOT NULL,
    id_origen INT NOT NULL,
    id_aeropuerto INT NOT NULL,
    hora_partida TIME,
    hora_llegada TIME,
    duracion_minutos INT,
    activa BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_origen) REFERENCES origen(id_origen),
    FOREIGN KEY (id_aeropuerto) REFERENCES aeropuerto(id_aeropuerto)
);

-- 6. TABLA VUELO (CORREGIDA)
CREATE TABLE vuelo (
    id_vuelo INT AUTO_INCREMENT PRIMARY KEY,
    callsign VARCHAR(10),
    id_aeropuerto_origen INT,
    id_aeropuerto_destino INT,
    id_estado INT,
    latitud DECIMAL(10,6),
    longitud DECIMAL(10,6),
    altitud INT,
    velocidad DECIMAL(8,2),
    hora_actualizacion TIMESTAMP,
    es_llegada_cdmx BOOLEAN,
    es_salida_cdmx BOOLEAN,
    distancia_a_cdmx DECIMAL(8,2),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_aeropuerto_origen) REFERENCES aeropuerto(id_aeropuerto),
    FOREIGN KEY (id_aeropuerto_destino) REFERENCES aeropuerto(id_aeropuerto),
    FOREIGN KEY (id_estado) REFERENCES estado(id_estado)
);
