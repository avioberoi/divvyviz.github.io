import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import AnimatedMarker from 'react-leaflet-animated-marker';
import 'leaflet/dist/leaflet.css';

export default function MapView() {
  const [trips, setTrips] = useState([]);

  useEffect(() => {
    fetch('https://data.cityofchicago.org/resource/fg6s-gzvg.json?$limit=1000')
      .then(r => r.json())
      .then(d => setTrips(d.filter(t => t.from_latitude && t.to_latitude)));
  }, []);

  return (
    <>
      <h2>Live Map of Trips</h2>
      <MapContainer
        center={[41.8781, -87.6298]}
        zoom={12}
        style={{ height:'600px', borderRadius:8 }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
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
              iconSize: [32,32]
            }}
          />
        ))}
      </MapContainer>
    </>
  );
}
