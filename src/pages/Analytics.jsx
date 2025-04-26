import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  BarChart, Bar, Legend, ResponsiveContainer
} from 'recharts';
import { useEffect, useState } from 'react';

export default function Analytics() {
  const [data, setData] = useState([]);

  useEffect(() => {
    // fetch aggregated hourly stats from backend or compute here
    fetch('/api/hourly-stats')
      .then(r=>r.json()).then(setData);
  }, []);

  return (
    <>
      <h2>Analytics</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3"/>
          <XAxis dataKey="hour" />
          <YAxis yAxisId="left" />
          <YAxis yAxisId="right" orientation="right" />
          <Tooltip />
          <Legend />
          <Line yAxisId="left" type="monotone" dataKey="tripCount" name="Trip Count" stroke="#8884d8"/>
          <Line yAxisId="right" type="monotone" dataKey="avgDuration" name="Avg Duration (s)" stroke="#82ca9d"/>
        </LineChart>
      </ResponsiveContainer>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3"/>
          <XAxis dataKey="hour" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="tripCount" fill="#413ea0" name="Trip Count"/>
        </BarChart>
      </ResponsiveContainer>
    </>
  );
}
//``` :contentReference[oaicite:19]{index=19} :contentReference[oaicite:20]{index=20}
