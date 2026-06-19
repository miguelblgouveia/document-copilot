import { useState } from 'react'

type ChatMessageProps = {
  role: 'user' | 'assistant'
  content: string
  timestamp?: Date
}

export function ChatMessage({ role, content, timestamp }: ChatMessageProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  
  const toggleExpand = () => {
    setIsExpanded(!isExpanded)
  }

  return (
    <div className={`flex ${role === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
      <div 
        className={`max-w-[80%] rounded-lg p-4 ${
          role === 'user' 
            ? 'bg-blue-500 text-white rounded-br-none' 
            : 'bg-gray-100 text-gray-800 rounded-bl-none'
        }`}
      >
        <div className="flex items-center mb-1">
          <span className="font-semibold mr-2">
            {role === 'user' ? 'You' : 'Assistant'}
          </span>
          {timestamp && (
            <span className="text-xs opacity-70">
              {timestamp.toLocaleTimeString()}
            </span>
          )}
        </div>
        <div 
          className={`whitespace-pre-wrap ${isExpanded ? '' : 'line-clamp-3'}`}
        >
          {content}
        </div>
        {!isExpanded && content.length > 200 && (
          <button 
            onClick={toggleExpand}
            className="text-xs mt-1 text-blue-500 hover:underline"
          >
            Show more
          </button>
        )}
      </div>
    </div>
  )
}