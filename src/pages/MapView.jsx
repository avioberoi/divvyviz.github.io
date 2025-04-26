import { MapContainer, TileLayer } from 'react-leaflet';
import AnimatedMarker from 'react-leaflet-animated-marker';
import { useEffect, useState } from 'react';
import 'leaflet/dist/leaflet.css';

export default function MapView() {
  const [trips, setTrips] = useState([]);

  useEffect(() => {
    fetch('https://data.cityofchicago.org/resource/fg6s-gzvg.json?$limit=2000')
      .then(r => r.json())
      .then(d => setTrips(d.filter(t=>t.from_latitude&&t.to_latitude)));
  }, []);

  return (
    <>
      <h2>Live Trip Map</h2>
      <MapContainer center={[41.8781, -87.6298]} zoom={12} style={{ height: 600 }}>
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {trips.map(t => (
          <AnimatedMarker
            key={t.trip_id}
            positions={[
              [t.from_latitude, t.from_longitude],
              [t.to_latitude, t.to_longitude]
            ]}
            duration={t.trip_duration * 1000}
            icon={{
              iconUrl: 'https://cdn-icons-png.flaticon.com/512/684/684908.png',
              iconSize: [32, 32]
            }}
          />
        ))}
      </MapContainer>
    </>
  );
}
//``` :contentReference[oaicite:17]{index=17} :contentReference[oaicite:18]{index=18}



