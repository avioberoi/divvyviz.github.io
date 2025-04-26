// src/App.js
import React from 'react';
import { Layout, Menu } from 'antd';
import { Routes, Route, Link } from 'react-router-dom';

import Overview  from './pages/Overview';
import MapView   from './pages/MapView';
import Analytics from './pages/Analytics';

const { Sider, Header, Content, Footer } = Layout;

export default function App() {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider breakpoint="lg" collapsedWidth="0">
        <div className="logo" style={{ color:'#fff', padding:'16px', textAlign:'center' }}>
          🚲 DivvyDash
        </div>
        <Menu theme="dark" mode="inline" defaultSelectedKeys={['overview']}>
          <Menu.Item key="overview"><Link to="/">Overview</Link></Menu.Item>
          <Menu.Item key="map"><Link to="/map">Map</Link></Menu.Item>
          <Menu.Item key="analytics"><Link to="/analytics">Analytics</Link></Menu.Item>
        </Menu>
      </Sider>

      <Layout>
        <Header style={{ background:'#fff', padding:'0 24px' }}>
          <h2 style={{ margin:0 }}>Divvy Trips Dashboard</h2>
        </Header>

        <Content style={{ margin:'24px 16px 0' }}>
          <Routes>
            <Route path="/"        element={<Overview />} />
            <Route path="/map"     element={<MapView />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </Content>

        <Footer style={{ textAlign:'center' }}>
          © 2025 Transit Hacks — Built with UChicago APIs
        </Footer>
      </Layout>
    </Layout>
  );
}
