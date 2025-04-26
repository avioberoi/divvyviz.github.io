// Initialize map centered on Chicago  
const map = L.map('map').setView([41.8781, -87.6298], 12);

// Add OSM basemap  
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

/**
 * Fetch a small sample of recent Divvy trips from Chicago Data Portal
 * (limit=50 for demo) :contentReference[oaicite:7]{index=7}
 */
fetch('https://data.cityofchicago.org/resource/fg6s-gzvg.json?$limit=50')
  .then(res => res.json())
  .then(trips => {
    trips.forEach(trip => {
      // Parse coords
      const from = [parseFloat(trip.from_latitude), parseFloat(trip.from_longitude)];
      const to   = [parseFloat(trip.to_latitude),   parseFloat(trip.to_longitude)];
      if (!from[0] || !to[0]) return;

      // Create a MovingMarker instance along the two-point polyline :contentReference[oaicite:8]{index=8}
      const marker = L.Marker.movingMarker(
        [from, to],
        [trip.trip_duration * 1000], // duration in ms
        { icon: L.divIcon({ className: 'bike-icon' }) }
      ).addTo(map);

      // Optional: remove when animation ends
      marker.on('end', () => map.removeLayer(marker));
      marker.start();
    });
  })
  .catch(err => console.error('Error loading trips:', err));
