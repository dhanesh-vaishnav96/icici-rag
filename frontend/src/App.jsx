import { useState, useCallback } from 'react'
import './App.css'
import ChatWindow from './components/ChatWindow'
import ChatInput from './components/ChatInput'

const API_URL = 'http://localhost:8000/chat'

let msgId = 0

export default function App() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  const sendMessage = useCallback(async (question) => {
    // Add user message
    const userMsg = {
      id: ++msgId,
      role: 'user',
      content: question,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMsg])
    setIsLoading(true)

    // Abort after 90 seconds so the UI never hangs forever
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 90_000)

    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
        signal: controller.signal,
      })

      if (!res.ok) {
        throw new Error(`Server error: ${res.status} ${res.statusText}`)
      }

      const data = await res.json()

      setMessages((prev) => [
        ...prev,
        {
          id: ++msgId,
          role: 'bot',
          content: data.answer ?? 'No response from server.',
          timestamp: new Date(),
          isError: false,
        },
      ])
    } catch (err) {
      const isTimeout = err.name === 'AbortError'
      setMessages((prev) => [
        ...prev,
        {
          id: ++msgId,
          role: 'bot',
          content: isTimeout
            ? '⏱️ The request took too long. Please try again in a moment.'
            : `⚠️ ${err.message || 'Could not reach the backend. Make sure the server is running on port 8000.'}`,
          timestamp: new Date(),
          isError: true,
        },
      ])
    } finally {
      clearTimeout(timeoutId)
      setIsLoading(false)
    }
  }, [])

  return (
    <div className="app-shell">
      {/* Header */}
      <header className="header">
        <div className="header-icon">🧠</div>
        <div className="header-info">
          <h1>RAG Document Assistant</h1>
          <p>
            <span className="status-dot" />
            Powered by Gemini + Qdrant
          </p>
        </div>
      </header>

      {/* Chat Messages */}
      <ChatWindow
        messages={messages}
        isLoading={isLoading}
        onSuggestion={sendMessage}
      />

      {/* Input */}
      <ChatInput onSend={sendMessage} disabled={isLoading} />
    </div>
  )
}
