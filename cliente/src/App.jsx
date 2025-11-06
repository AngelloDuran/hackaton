import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import axios from "axios";
import L from "leaflet";

const avionIcon = new L.Icon({
  iconUrl:
    "https://cdn-icons-png.flaticon.com/512/3125/3125713.png",
  iconSize: [30, 30],
});

function App() {
  const [vuelos, setVuelos] = useState([]);

  useEffect(() => {
    const obtenerVuelos = async () => {
      try {
        const res = await axios.get("http://127.0.0.1:5000/vuelos_cdmx");
        setVuelos(res.data.vuelos || []);
      } catch (err) {
        console.error("Error al obtener vuelos:", err);
      }
    };

    obtenerVuelos();
    const intervalo = setInterval(obtenerVuelos, 10000); // Actualiza cada 10s
    return () => clearInterval(intervalo);
  }, []);

  return (
    <div style={{ height: "100vh", width: "100%" }}>
      <MapContainer
        center={[19.4361, -99.0719]} // CDMX
        zoom={10}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {vuelos.map((v, i) => (
          v.latitud && v.longitud && (
            <Marker
              key={i}
              position={[v.latitud, v.longitud]}
              icon={avionIcon}
            >
              <Popup>
                ✈️ <b>{v.callsign || "Sin identificación"}</b><br />
                País: {v.pais_origen}<br />
                Altitud: {v.altitud?.toFixed(0)} m<br />
                Velocidad: {v.velocidad?.toFixed(0)} km/h
              </Popup>
            </Marker>
          )
        ))}
      </MapContainer>
    </div>
  );
}

export default App;
