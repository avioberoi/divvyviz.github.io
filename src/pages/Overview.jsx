import React from 'react';
import { Row, Col, Typography, Image } from 'antd';
import StatisticCard from '../components/StatisticCard';

const { Title, Paragraph } = Typography;

export default function Overview() {
  // Replace with real fetched stats later
  const stats = [
    { title:'Total Trips',           value:21_200_000 },
    { title:'Avg Trip Duration (s)', value: 560 },
    { title:'Active Stations',       value: 700 },
  ];

  return (
    <>
      <Title level={2}>Overview</Title>
      <Paragraph>
        A high-level snapshot of Divvy usage: total trips, average durations, and station coverage.
      </Paragraph>

      <Row gutter={[16,16]}>
        {stats.map(s => (
          <Col key={s.title}>
            <StatisticCard {...s} />
          </Col>
        ))}
      </Row>

      <Image
        width="100%"
        style={{ marginTop:24, borderRadius:8 }}
        src="https://placekitten.com/800/300"
        alt="Decorative graphic"
      />
    </>
  );
}
