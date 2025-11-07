import { useEffect, useState, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, Polyline } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import axios from "axios";
import L from "leaflet";

const avionIcon = new L.Icon({
  iconUrl: "https://cdn-icons-png.flaticon.com/512/3125/3125713.png",
  iconSize: [30, 30],
});

const destinoIcon = new L.Icon({
  iconUrl: "https://cdn-icons-png.flaticon.com/512/684/684908.png",
  iconSize: [20, 20],
});

function App() {
  const [vuelos, setVuelos] = useState([]);
  const vuelosRef = useRef({}); // Para guardar posiciones actuales para animación

  useEffect(() => {
    const obtenerVuelos = async () => {
      try {
        const res = await axios.get("http://127.0.0.1:5000/api/vuelos");
        const nuevosVuelos = res.data.vuelos || [];

        // Actualizamos posiciones suavemente
        const actualizados = nuevosVuelos.map((v) => {
          const id = v.callsign || Math.random(); // identificar vuelo
          const latNew = Number(v.latitud);
          const lonNew = Number(v.longitud);
          if (isNaN(latNew) || isNaN(lonNew)) return null;

          // Si ya tenemos posición previa, usamos la actual, si no usamos la nueva
          const posActual = vuelosRef.current[id] || [latNew, lonNew];
          vuelosRef.current[id] = posActual; // aseguramos que exista
          return { ...v, posActual };
        }).filter(Boolean);

        setVuelos(actualizados);
      } catch (err) {
        console.error("Error al obtener vuelos:", err);
      }
    };

    obtenerVuelos();
    const intervalo = setInterval(obtenerVuelos, 5000);
    return () => clearInterval(intervalo);
  }, []);

  // Animación de movimiento
  useEffect(() => {
    const animar = setInterval(() => {
      setVuelos((prev) =>
        prev.map((v) => {
          const latDestino = Number(v.latitud);
          const lonDestino = Number(v.longitud);
          if (isNaN(latDestino) || isNaN(lonDestino)) return v;

          let [latActual, lonActual] = v.posActual;

          // Interpolación simple (0.05 = velocidad de transición)
          latActual += (latDestino - latActual) * 0.05;
          lonActual += (lonDestino - lonActual) * 0.05;

          vuelosRef.current[v.callsign] = [latActual, lonActual];
          return { ...v, posActual: [latActual, lonActual] };
        })
      );
    }, 50); // 20 FPS
    return () => clearInterval(animar);
  }, []);

  const formatNumber = (value) => {
    const num = Number(value);
    return !isNaN(num) ? num.toFixed(0) : "-";
  };
  const safeString = (value) => (value ? value : "-");

  return (
    <div style={{ height: "100vh", width: "100%", margin: 0, padding: 0 }}>
      <MapContainer
        center={[19.4361, -99.0719]}
        zoom={5}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {vuelos.map((v, i) => {
          const [lat, lon] = v.posActual;
          const latDest = Number(v.lat_destino);
          const lonDest = Number(v.lon_destino);

          return (
            <div key={i}>
              {/* Marker del avión */}
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

              {/* Ruta hacia destino */}
              {!isNaN(latDest) && !isNaN(lonDest) && (
                <>
                  <Polyline
                    positions={[
                      [lat, lon],
                      [latDest, lonDest]
                    ]}
                    color="blue"
                    weight={2}
                    dashArray="5,5"
                  />
                  <Marker position={[latDest, lonDest]} icon={destinoIcon}>
                    <Popup>
                      🛬 Destino aproximado
                      <br />
                      {safeString(v.destino_nombre || "Desconocido")}
                    </Popup>
                  </Marker>
                </>
              )}
            </div>
          );
        })}
      </MapContainer>
    </div>
  );
}

export default App;
