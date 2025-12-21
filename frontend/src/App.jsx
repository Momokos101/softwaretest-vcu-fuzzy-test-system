import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Layout } from 'antd'
import AppLayout from './components/Layout'
import HomePage from './pages/HomePage'
import TestPlanPage from './pages/TestPlanPage'
import TestTaskPage from './pages/TestTaskPage'
import MonitoringPage from './pages/MonitoringPage'
import ReportPage from './pages/ReportPage'

const { Content } = Layout

function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/test-plans" element={<TestPlanPage />} />
          <Route path="/test-tasks" element={<TestTaskPage />} />
          <Route path="/monitoring/:taskId" element={<MonitoringPage />} />
          <Route path="/reports" element={<ReportPage />} />
        </Routes>
      </AppLayout>
    </Router>
  )
}

export default App

