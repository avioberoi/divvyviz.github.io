// Shared utilities inspired by mbtaviz/common.js :contentReference[oaicite:13]{index=13}
const VIZ = {
    pageHeight: () => window.innerHeight,
    wrap: (text, width) => { /* omitted for brevity */ },
  };
  
  // Initialize map (Leaflet) :contentReference[oaicite:14]{index=14}
  const map = L.map('map').setView([41.8781, -87.6298], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);
  
  // Configure date slider (noUiSlider) :contentReference[oaicite:15]{index=15}
  const dateSlider = document.getElementById('date-slider');
  noUiSlider.create(dateSlider, {
    start: [0, 23],
    connect: true,
    range: { min: 0, max: 23 },
    tooltips: [true, true]
  });
  let currentRange = [0, 23];
  dateSlider.noUiSlider.on('update', v => {
    currentRange = v.map(Number);
    updateVisuals();
  });
  
  // Chart.js dual-axis config :contentReference[oaicite:16]{index=16}
  const ctx = document.getElementById('tripChart').getContext('2d');
  const tripChart = new Chart(ctx, {
    type: 'line',
    data: { labels: [], datasets: [
        { label: 'Trip Count', yAxisID: 'y', data: [], fill: false },
        { label: 'Avg Duration (s)', yAxisID: 'y1', data: [], fill: false }
      ]
    },
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      scales: {
        y: { type: 'linear', position: 'left', beginAtZero: true },
        y1: {
          type: 'linear', position: 'right',
          grid: { drawOnChartArea: false }
        }
      }
    }
  });
  
  // Load sample data with progress (mbtaviz/dataloader.js style) :contentReference[oaicite:17]{index=17}
  async function loadData() {
    const indicator = document.getElementById('loading-indicator');
    const res = await fetch('https://data.cityofchicago.org/resource/fg6s-gzvg.json?$limit=5000');
    const reader = res.body.getReader();
    const contentLength = +res.headers.get('Content-Length');
    let received = 0, chunks = [];
    while(true) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value);
      received += value.length;
      indicator.textContent = `Loading… ${Math.floor(100 * received/contentLength)}%`;
    }
    const text = new TextDecoder("utf-8")
                      .decode(new Uint8Array(chunks.flat()));
    return JSON.parse(text);
  }
  
  // State
  let trips = [];
  
  // After data loaded, kick off first render
  loadData().then(data => {
    trips = data.filter(d=>d.from_latitude && d.to_latitude);
    document.getElementById('loading-indicator').style.display = 'none';
    updateVisuals();
  });
  
  // Re-render map & chart when filters or slider change
  function updateVisuals() {
    // Clear existing markers
    map.eachLayer(l => (l instanceof L.Marker) && map.removeLayer(l));
  
    // Filter by time, gender, user type
    const ui = document.getElementById('user-type').value;
    const g  = document.getElementById('gender').value;
    const filtered = trips.filter(d => {
      const hr = new Date(d.start_time).getHours();
      if (hr < currentRange[0] || hr > currentRange[1]) return false;
      if (ui!=='All'   && d.user_type !== ui) return false;
      if (g!=='All'    && d.gender    !== g) return false;
      return true;
    });
  
    // Animate each trip as a moving marker :contentReference[oaicite:18]{index=18}
    filtered.forEach(d => {
      const from = [ +d.from_latitude, +d.from_longitude ];
      const to   = [ +d.to_latitude,   +d.to_longitude ];
      const m = L.movingMarker([ from, to ], [ d.trip_duration*1000 ], {
        icon: L.divIcon({ className: 'bike-icon' })
      }).addTo(map);
      m.on('end', () => map.removeLayer(m));
      m.start();
    });
  
    // Aggregate for chart
    const counts = {}, durations = {};
    filtered.forEach(d => {
      const h = new Date(d.start_time).getHours();
      counts[h] = (counts[h]||0) + 1;
      durations[h] = (durations[h]||0) + +d.trip_duration;
    });
    const hours = Array.from({length:24}, (_,i)=>i);
    tripChart.data.labels = hours.map(h=>`${h}:00`);
    tripChart.data.datasets[0].data = hours.map(h=>counts[h]||0);
    tripChart.data.datasets[1].data = hours.map(h=> {
      const c = counts[h]||1;
      return Math.round((durations[h]||0)/c);
    });
    tripChart.update();
  }  