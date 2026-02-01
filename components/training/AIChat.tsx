'use client';

import { Card, CardHeader, CardContent, Button } from '@/components/ui';
import { useState } from 'react';

interface AIChatProps {
  planId?: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export function AIChat({ planId }: AIChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: '你好!我是你的AI训练助手。有任何关于训练计划的问题都可以问我!',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const quickQuestions = [
    '如何提高训练效果?',
    '休息日该做什么?',
    '饮食建议有哪些?',
    '如何防止受伤?',
  ];

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `关于"${input}",我的建议是:保持训练的一致性很重要,同时要注意循序渐进,避免过度训练。记得合理安排休息和营养补充。`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1500);
  };

  const handleQuickQuestion = (question: string) => {
    setInput(question);
  };

  return (
    <Card className="h-[600px] flex flex-col">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-blue-600 flex items-center justify-center text-white text-lg">
            🤖
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-dark-900">AI 训练助手</h3>
            <div className="flex items-center gap-2 text-xs text-dark-600">
              <span className="w-2 h-2 rounded-full bg-green-500" />
              <span>在线</span>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-4 overflow-hidden">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto mb-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[80%] px-4 py-2 rounded-2xl ${
                  message.role === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'bg-dark-100 text-dark-900'
                }`}
              >
                <p className="text-sm">{message.content}</p>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-dark-100 px-4 py-2 rounded-2xl">
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 bg-dark-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-dark-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  <div className="w-2 h-2 bg-dark-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Quick Questions */}
        {messages.length <= 1 && (
          <div className="mb-4">
            <p className="text-xs text-dark-600 mb-2">常见问题:</p>
            <div className="flex flex-wrap gap-2">
              {quickQuestions.map((question) => (
                <button
                  key={question}
                  onClick={() => handleQuickQuestion(question)}
                  className="px-3 py-1.5 text-xs bg-primary-50 text-primary-700 rounded-full hover:bg-primary-100 transition-colors"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="输入您的问题..."
            className="flex-1 px-4 py-2 border border-dark-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <Button
            variant="primary"
            size="md"
            onClick={handleSend}
            disabled={!input.trim() || isTyping}
          >
            发送
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
