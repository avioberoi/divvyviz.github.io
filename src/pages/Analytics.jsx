import React, { useEffect, useState } from 'react';
import {
  ResponsiveContainer, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  BarChart, Bar
} from 'recharts';

export default function Analytics() {
  const [data, setData] = useState([]);

  useEffect(() => {
    // In a real app, replace with an actual endpoint or local computation
    fetch('/api/hourly-stats')
      .then(r => r.json())
      .then(setData);
  }, []);

  return (
    <>
      <h2>Hourly Analytics</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="hour" />
          <YAxis yAxisId="left" label={{ value:'Trips', angle:-90, position:'insideLeft' }} />
          <YAxis yAxisId="right" orientation="right" label={{ value:'Avg Duration', angle:90, position:'insideRight' }}/>
          <Tooltip />
          <Legend />
          <Line yAxisId="left" dataKey="tripCount" name="Trip Count" stroke="#8884d8" />
          <Line yAxisId="right" dataKey="avgDuration" name="Avg Duration (s)" stroke="#82ca9d" />
        </LineChart>
      </ResponsiveContainer>

      <ResponsiveContainer width="100%" height={300} style={{ marginTop:24 }}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="hour" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="tripCount" fill="#413ea0" name="Trip Count" />
        </BarChart>
      </ResponsiveContainer>
    </>
  );
}
