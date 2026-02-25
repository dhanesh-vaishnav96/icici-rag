import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export default function MessageBubble({ role, content, timestamp, isError }) {
  const isUser = role === 'user'

  return (
    <div className={`message-row ${isUser ? 'user' : 'bot'}`}>
      <div className={`avatar ${isUser ? 'user' : 'bot'}`}>
        {isUser ? '👤' : '🤖'}
      </div>

      <div>
        <div className={`bubble ${isUser ? 'user' : isError ? 'error' : 'bot'}`}>
          {isUser ? (
            content
          ) : (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {content}
            </ReactMarkdown>
          )}
        </div>
        <div className="timestamp">{formatTime(timestamp)}</div>
      </div>
    </div>
  )
}
