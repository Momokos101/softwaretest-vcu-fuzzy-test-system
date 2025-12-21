/**
 * WebSocket工具类
 * 用于实时监控测试任务状态
 */
class WebSocketManager {
  constructor() {
    this.ws = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
    this.listeners = new Map()
  }

  connect(taskId, onMessage, onError) {
    const wsUrl = `ws://localhost:8000/ws/test-tasks/${taskId}`
    
    try {
      this.ws = new WebSocket(wsUrl)
      
      this.ws.onopen = () => {
        console.log('WebSocket连接已建立')
        this.reconnectAttempts = 0
      }
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (onMessage) {
            onMessage(data)
          }
          // 触发所有监听器
          this.listeners.forEach((callback) => {
            callback(data)
          })
        } catch (error) {
          console.error('解析WebSocket消息失败:', error)
        }
      }
      
      this.ws.onerror = (error) => {
        console.error('WebSocket错误:', error)
        if (onError) {
          onError(error)
        }
      }
      
      this.ws.onclose = () => {
        console.log('WebSocket连接已关闭')
        this.attemptReconnect(taskId, onMessage, onError)
      }
    } catch (error) {
      console.error('WebSocket连接失败:', error)
      if (onError) {
        onError(error)
      }
    }
  }

  attemptReconnect(taskId, onMessage, onError) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      setTimeout(() => {
        console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
        this.connect(taskId, onMessage, onError)
      }, this.reconnectDelay * this.reconnectAttempts)
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket未连接，无法发送消息')
    }
  }

  close() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.listeners.clear()
  }

  addListener(key, callback) {
    this.listeners.set(key, callback)
  }

  removeListener(key) {
    this.listeners.delete(key)
  }
}

export default new WebSocketManager()

