const WS_URL = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/kernel/ws`

export function createChatSocket(onMessage) {
  let ws = null
  let reconnectTimer = null
  let closed = false

  function connect() {
    if (closed) return
    ws = new WebSocket(WS_URL)

    ws.onopen = () => {
      onMessage({ type: 'connected' })
    }

    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)
        onMessage(data)
      } catch {
        // ignore
      }
    }

    ws.onclose = () => {
      onMessage({ type: 'disconnected' })
      if (!closed) {
        reconnectTimer = setTimeout(connect, 3000)
      }
    }

    ws.onerror = () => {
      ws?.close()
    }
  }

  connect()

  return {
    send(text) {
      if (ws?.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ input: text, channel: 'web' }))
      }
    },
    close() {
      closed = true
      clearTimeout(reconnectTimer)
      ws?.close()
    },
  }
}
