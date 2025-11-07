import React, { useEffect, useState, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, Polyline } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import axios from "axios";
import L from "leaflet";
import "./Home.css"; // Estilos personalizados
import {
  FaPlane,
  FaPlaneDeparture,
  FaPlaneArrival,
  FaCalendarAlt,
  FaTimesCircle,
  FaRandom,
  FaCircle,
} from "react-icons/fa";

// === ICONOS PARA MAPA ===
const avionIcon = new L.Icon({
  iconUrl: "https://cdn-icons-png.flaticon.com/512/3125/3125713.png",
  iconSize: [30, 30],
});

const aeropuertoIcon = new L.Icon({
  iconUrl: "https://cdn-icons-png.flaticon.com/512/684/684908.png",
  iconSize: [25, 25],
});

// === TARJETAS DE ESTADÍSTICAS ===
const StatCard = ({ title, value, icon, color }) => (
  <div className="stat-card">
    <div className="stat-card-icon" style={{ backgroundColor: color }}>
      {icon}
    </div>
    <div className="stat-card-text">
      <div className="stat-card-value">{value}</div>
      <div className="stat-card-title">{title}</div>
    </div>
  </div>
);

const statColors = {
  vuelosActivos: "#0a4da2",
  enVuelo: "#27ae60",
  aterrizados: "#8e44ad",
  programados: "#2980b9",
  cancelados: "#c0392b",
  desviados: "#f39c12",
};

// === COMPONENTE PRINCIPAL ===
export default function Home() {
  const [vuelos, setVuelos] = useState([]);
  const vuelosRef = useRef({});
  const [stats, setStats] = useState({});
  const [error, setError] = useState(null);
  const [currentTime, setCurrentTime] = useState(new Date());

  // Actualizar reloj
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Obtener vuelos y estadísticas
  useEffect(() => {
    const obtenerVuelos = async () => {
      try {
        const res = await axios.get("http://127.0.0.1:5000/api/vuelos", { withCredentials: true });
        const nuevosVuelos = res.data.vuelos || [];

        const actualizados = nuevosVuelos
          .map((v) => {
            const id = v.callsign || Math.random();
            const latNew = Number(v.latitud);
            const lonNew = Number(v.longitud);
            if (isNaN(latNew) || isNaN(lonNew)) return null;

            const posActual = vuelosRef.current[id] || [latNew, lonNew];
            vuelosRef.current[id] = posActual;
            return { ...v, posActual };
          })
          .filter(Boolean);

        setVuelos(actualizados);
        setStats(res.data.stats || {});
      } catch (err) {
        console.error("Error al obtener vuelos:", err);
        setError("No se pudieron cargar los datos de vuelos.");
      }
    };

    obtenerVuelos();
    const intervalo = setInterval(obtenerVuelos, 5000);
    return () => clearInterval(intervalo);
  }, []);

  // Animación del movimiento
  useEffect(() => {
    const animar = setInterval(() => {
      setVuelos((prev) =>
        prev.map((v) => {
          const latDestino = Number(v.latitud);
          const lonDestino = Number(v.longitud);
          if (isNaN(latDestino) || isNaN(lonDestino)) return v;

          let [latActual, lonActual] = v.posActual;
          latActual += (latDestino - latActual) * 0.05;
          lonActual += (lonDestino - lonActual) * 0.05;

          vuelosRef.current[v.callsign] = [latActual, lonActual];
          return { ...v, posActual: [latActual, lonActual] };
        })
      );
    }, 50);
    return () => clearInterval(animar);
  }, []);

  const formatNumber = (value) => {
    const num = Number(value);
    return !isNaN(num) ? num.toFixed(0) : "-";
  };
  const safeString = (value) => (value ? value : "-");

  return (
    <div className="main-content">
      {/* Header */}
      <header className="header">
        <div>
          <h1 className="header-title">Monitoreo de Tráfico Aéreo CDMX</h1>
          <p className="header-subtitle">Aeropuerto Internacional de la Ciudad de México</p>
        </div>
        <div className="time-box">
          <div className="time-actual">
            {currentTime.toLocaleTimeString("es-MX", {
              hour: "2-digit",
              minute: "2-digit",
              second: "2-digit",
              hour12: true,
            })}
          </div>
          <div className="time-fecha">
            {currentTime.toLocaleDateString("es-MX", {
              weekday: "long",
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </div>
        </div>
      </header>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {/* Tarjetas */}
      <div className="stats-grid">
        <StatCard title="Vuelos Activos" value={stats.vuelosActivos || vuelos.length} icon={<FaPlane />} color={statColors.vuelosActivos} />
        <StatCard title="En Vuelo" value={stats.enVuelo || 0} icon={<FaPlaneDeparture />} color={statColors.enVuelo} />
        <StatCard title="Aterrizados" value={stats.aterrizados || 0} icon={<FaPlaneArrival />} color={statColors.aterrizados} />
        <StatCard title="Programados" value={stats.programados || 0} icon={<FaCalendarAlt />} color={statColors.programados} />
        <StatCard title="Cancelados" value={stats.cancelados || 0} icon={<FaTimesCircle />} color={statColors.cancelados} />
        <StatCard title="Desviados" value={stats.desviados || 0} icon={<FaRandom />} color={statColors.desviados} />
      </div>

      {/* Mapa */}
      <div className="section-container">
        <h3 className="section-title">
          Vista en Tiempo Real{" "}
          <span className="update-status">
            <FaCircle size="0.6rem" /> &nbsp;Actualización cada 5s
          </span>
        </h3>

        <div className="map-wrapper">
          <MapContainer center={[19.4361, -99.0719]} zoom={6} className="map-container">
            <TileLayer
              attribution="&copy; OpenStreetMap contributors"
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {vuelos.map((v, i) => {
              const [lat, lon] = v.posActual;
              const latOrigen = Number(v.lat_origen);
              const lonOrigen = Number(v.lon_origen);

              return (
                <React.Fragment key={i}>
                  <Marker position={[lat, lon]} icon={avionIcon}>
                    <Popup>
                      ✈️ <b>{safeString(v.callsign)}</b>
                      <br />
                      País: {safeString(v.pais_origen)}
                      <br />
                      Altitud: {formatNumber(v.altitud)} m
                      <br />
                      Velocidad: {formatNumber(v.velocidad)} km/h
                    </Popup>
                  </Marker>

                  {!isNaN(latOrigen) && !isNaN(lonOrigen) && (
                    <>
                      <Polyline
                        positions={[
                          [latOrigen, lonOrigen],
                          [lat, lon],
                        ]}
                        color="green"
                        weight={2}
                        dashArray="5,5"
                      />
                      <Marker position={[latOrigen, lonOrigen]} icon={aeropuertoIcon}>
                        <Popup>🛫 {safeString(v.aeropuerto_origen || "Desconocido")}</Popup>
                      </Marker>
                    </>
                  )}
                </React.Fragment>
              );
            })}
          </MapContainer>
        </div>
      </div>
    </div>
  );
}
