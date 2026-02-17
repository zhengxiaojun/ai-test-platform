import { Link, Outlet, useLocation } from 'umi';
import { Layout, Menu } from 'antd';
import { HomeOutlined, ApiOutlined, FileTextOutlined, PlayCircleOutlined, BarChartOutlined, MenuFoldOutlined, MenuUnfoldOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { useState } from 'react';

const { Header, Content, Sider } = Layout;

const menuItems: MenuProps['items'] = [
  {
    key: '/',
    icon: <HomeOutlined />,
    label: <Link to="/">AI助手</Link>,
  },
  {
    key: '/interface',
    icon: <ApiOutlined />,
    label: <Link to="/interface">接口管理</Link>,
  },
  {
    key: '/testcase',
    icon: <FileTextOutlined />,
    label: <Link to="/testcase">测试用例</Link>,
  },
  {
    key: '/execution',
    icon: <PlayCircleOutlined />,
    label: <Link to="/execution">测试执行</Link>,
  },
  {
    key: '/report',
    icon: <BarChartOutlined />,
    label: <Link to="/report">测试报告</Link>,
  },
];

export default function BasicLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsed={collapsed}
        trigger={null}
        width={200}
        style={{
          background: '#fff',
          boxShadow: '2px 0 8px 0 rgba(29,35,41,.05)',
        }}
      >
        <div style={{
          height: '64px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: collapsed ? '14px' : '16px',
          fontWeight: 'bold',
          color: '#1890ff',
          transition: 'all 0.2s',
          padding: '0 16px',
        }}>
          {collapsed ? '🤖' : '🤖 AI测试平台'}
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          style={{
            height: 'calc(100% - 64px)',
            borderRight: 0,
          }}
          items={menuItems}
        />
      </Sider>
      <Layout>
        <Header style={{
          background: '#fff',
          padding: '0 24px',
          boxShadow: '0 1px 4px rgba(0,21,41,.08)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            {collapsed ? <MenuUnfoldOutlined
              style={{ fontSize: '18px', cursor: 'pointer' }}
              onClick={() => setCollapsed(false)}
            /> : <MenuFoldOutlined
              style={{ fontSize: '18px', cursor: 'pointer' }}
              onClick={() => setCollapsed(true)}
            />}
          </div>
        </Header>
        <Content style={{
          margin: '16px',
          background: '#f0f2f5',
        }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}

