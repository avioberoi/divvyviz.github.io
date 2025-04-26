import React from 'react';
import { Card, Statistic } from 'antd';

export default function StatisticCard({ title, value, suffix, prefix }) {
  return (
    <Card style={{ width:240, marginBottom:16 }}>
      <Statistic title={title} value={value} suffix={suffix} prefix={prefix} />
    </Card>
  );
}
