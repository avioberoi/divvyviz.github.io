import { Row, Col, Typography, Image } from 'antd';
import StatisticCard from '../components/StatisticCard';
const { Title, Paragraph } = Typography;

export default function Overview() {
  // dummy stats; in real useEffect fetch summary from API
  const stats = [
    { title: 'Total Trips',  value: 21200000, suffix: '' },
    { title: 'Average Duration', value: 560, suffix: 's' },
    { title: 'Active Stations',  value: 700, suffix: '' },
  ];

  return (
    <>
      <Title level={2}>Overview</Title>
      <Paragraph>
        This dashboard visualizes Divvy bike-sharing trips with real-time mapping and analytics.
      </Paragraph>
      <Row gutter={[16, 16]}>
        {stats.map(s => (
          <Col key={s.title}>
            <StatisticCard {...s} />
          </Col>
        ))} 
      </Row>
      <Image
        width={600}
        src="https://placekitten.com/800/400"
        alt="Sample promo image"
        style={{ margin: '24px auto', display: 'block' }}
      />
    </>
  );
}
