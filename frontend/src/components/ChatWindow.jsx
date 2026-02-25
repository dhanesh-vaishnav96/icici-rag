import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'

const SUGGESTIONS = [
    'What is this document about?',
    'Summarize the key points',
    'What are the main topics covered?',
    'Give me a brief overview',
]

export default function ChatWindow({ messages, isLoading, onSuggestion }) {
    const bottomRef = useRef(null)

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages, isLoading])

    if (messages.length === 0 && !isLoading) {
        return (
            <div className="chat-window">
                <div className="empty-state">
                    <div className="empty-icon">📄</div>
                    <h2>Ask me anything</h2>
                    <p>I've analyzed the document and I'm ready to answer your questions.</p>
                    <div className="suggestion-chips">
                        {SUGGESTIONS.map((s) => (
                            <button key={s} className="chip" onClick={() => onSuggestion(s)}>
                                {s}
                            </button>
                        ))}
                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className="chat-window">
            {messages.map((msg) => (
                <MessageBubble
                    key={msg.id}
                    role={msg.role}
                    content={msg.content}
                    timestamp={msg.timestamp}
                    isError={msg.isError}
                />
            ))}
            {isLoading && <TypingIndicator />}
            <div ref={bottomRef} />
        </div>
    )
}
