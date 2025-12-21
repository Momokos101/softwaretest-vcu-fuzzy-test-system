import { Layout, Menu } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  HomeOutlined,
  FileTextOutlined,
  PlayCircleOutlined,
  DashboardOutlined,
  FileDoneOutlined,
} from '@ant-design/icons'

const { Header, Content, Sider } = Layout

const menuItems = [
  {
    key: '/',
    icon: <HomeOutlined />,
    label: '首页',
  },
  {
    key: '/test-plans',
    icon: <FileTextOutlined />,
    label: '测试计划',
  },
  {
    key: '/test-tasks',
    icon: <PlayCircleOutlined />,
    label: '测试任务',
  },
  {
    key: '/reports',
    icon: <FileDoneOutlined />,
    label: '测试报告',
  },
]

function AppLayout({ children }) {
  const navigate = useNavigate()
  const location = useLocation()

  const handleMenuClick = ({ key }) => {
    navigate(key)
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ 
        background: '#001529', 
        color: '#fff',
        display: 'flex',
        alignItems: 'center',
        padding: '0 24px'
      }}>
        <h1 style={{ color: '#fff', margin: 0, fontSize: '20px' }}>
          VCU智能模糊测试系统
        </h1>
      </Header>
      <Layout>
        <Sider width={200} style={{ background: '#fff' }}>
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={handleMenuClick}
            style={{ height: '100%', borderRight: 0 }}
          />
        </Sider>
        <Layout style={{ padding: '24px' }}>
          <Content style={{ 
            background: '#fff',
            padding: '24px',
            margin: 0,
            minHeight: 280,
          }}>
            {children}
          </Content>
        </Layout>
      </Layout>
    </Layout>
  )
}

export default AppLayout

