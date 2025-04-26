import { Card, Statistic } from 'antd';

export default function StatisticCard({ title, value, suffix, prefix }) {
  return (
    <Card style={{ width: 240, margin: '0 16px' }}>
      <Statistic title={title} value={value} suffix={suffix} prefix={prefix} />
    </Card>
  );
}