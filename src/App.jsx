
import { Layout, Menu } from 'antd';
import { Routes, Route, Link } from 'react-router-dom';
import Overview from './pages/Overview';
import MapView  from './pages/MapView';
import Analytics from './pages/Analytics';

const { Header, Sider, Content, Footer } = Layout;

export default function App() {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider breakpoint="lg" collapsedWidth="0">
        <div className="logo">🚲 DivvyDash</div>
        <Menu theme="dark" mode="inline" defaultSelectedKeys={['1']}>
          <Menu.Item key="1"><Link to="/">Overview</Link></Menu.Item>
          <Menu.Item key="2"><Link to="/map">Map</Link></Menu.Item>
          <Menu.Item key="3"><Link to="/analytics">Analytics</Link></Menu.Item>
        </Menu>
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: 0 }}>
          <h2 style={{ marginLeft: 16 }}>Divvy Trips Dashboard</h2>
        </Header>
        <Content style={{ margin: '24px 16px 0' }}>
          <Routes>
            <Route path="/"       element={<Overview />} />
            <Route path="/map"    element={<MapView />}  />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          ©2025 Transit Hacks — Powered by UChicago APIs
        </Footer>
      </Layout>
    </Layout>
  );
}
//``` :contentReference[oaicite:15]{index=15} :contentReference[oaicite:16]{index=16}
