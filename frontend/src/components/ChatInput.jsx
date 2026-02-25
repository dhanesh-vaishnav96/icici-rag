import { useState, useRef, useEffect } from 'react'

const MAX_CHARS = 1000

export default function ChatInput({ onSend, disabled }) {
    const [text, setText] = useState('')
    const textareaRef = useRef(null)

    // Auto-resize textarea
    useEffect(() => {
        const ta = textareaRef.current
        if (!ta) return
        ta.style.height = 'auto'
        ta.style.height = Math.min(ta.scrollHeight, 140) + 'px'
    }, [text])

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    const handleSend = () => {
        const trimmed = text.trim()
        if (!trimmed || disabled) return
        onSend(trimmed)
        setText('')
        // Reset height
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto'
        }
    }

    const canSend = text.trim().length > 0 && !disabled && text.length <= MAX_CHARS

    return (
        <div className="input-area">
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 4 }}>
                <div className="input-wrapper">
                    <textarea
                        ref={textareaRef}
                        className="chat-textarea"
                        placeholder="Ask a question about the document…"
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        onKeyDown={handleKeyDown}
                        disabled={disabled}
                        rows={1}
                        maxLength={MAX_CHARS}
                        id="chat-input"
                        aria-label="Chat input"
                    />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span className="input-hint">Enter to send · Shift+Enter for new line</span>
                    <span
                        className="char-count"
                        style={{ color: text.length > MAX_CHARS * 0.9 ? '#f87171' : undefined }}
                    >
                        {text.length}/{MAX_CHARS}
                    </span>
                </div>
            </div>

            <button
                className="send-btn"
                onClick={handleSend}
                disabled={!canSend}
                aria-label="Send message"
                id="send-button"
            >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="22" y1="2" x2="11" y2="13" />
                    <polygon points="22 2 15 22 11 13 2 9 22 2" />
                </svg>
            </button>
        </div>
    )
}
