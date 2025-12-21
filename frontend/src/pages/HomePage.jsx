import { Card, Row, Col, Statistic } from 'antd'
import { FileTextOutlined, PlayCircleOutlined, CheckCircleOutlined } from '@ant-design/icons'

function HomePage() {
  return (
    <div>
      <h1>欢迎使用VCU智能模糊测试系统</h1>
      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic
              title="测试计划"
              value={0}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="运行中任务"
              value={0}
              prefix={<PlayCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="已完成任务"
              value={0}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default HomePage

