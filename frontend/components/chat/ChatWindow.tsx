'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, AlertCircle } from 'lucide-react';
import { api, ChatResponse } from '@/lib/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  pendingApproval?: Record<string, unknown> | null;
}

interface Props {
  customerId: string;
}

export default function ChatWindow({ customerId }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: `Hello! I'm TechKart AI Support. I can help you with orders, shipments, refunds, and product information. How can I assist you today?`,
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [threadId, setThreadId] = useState<string | undefined>();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res: ChatResponse = await api.chat({
        message: userMsg.content,
        customer_id: customerId,
        thread_id: threadId,
      });
      setThreadId(res.thread_id);
      const aiMsg: Message = {
        id: `ai-${Date.now()}`,
        role: 'assistant',
        content: res.response,
        timestamp: new Date(),
        pendingApproval: res.pending_approval,
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch {
      const errMsg: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-72px)]">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto chat-scrollbar p-4 space-y-5">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-3 msg-enter ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
            <div className={`flex-shrink-0 w-8 h-8 rounded-xl flex items-center justify-center shadow-sm ${
              msg.role === 'user'
                ? 'bg-gradient-to-br from-indigo-500 to-purple-600'
                : 'bg-gradient-to-br from-brand-100 to-brand-200 border border-brand-200'
            }`}>
              {msg.role === 'user'
                ? <User className="w-4 h-4 text-white" />
                : <Bot className="w-4 h-4 text-brand-600" />
              }
            </div>
            <div className={`max-w-[78%] rounded-2xl px-4 py-3 ${
              msg.role === 'user'
                ? 'bg-gradient-to-br from-indigo-600 to-purple-600 text-white rounded-tr-md shadow-lg shadow-indigo-200/40'
                : 'bg-white text-gray-800 border border-gray-100 rounded-tl-md shadow-sm'
            }`}>
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
              {msg.pendingApproval && (
                <div className="mt-3 p-3 bg-amber-50/90 border border-amber-200 rounded-xl">
                  <div className="flex items-center gap-2 mb-1">
                    <AlertCircle className="w-4 h-4 text-amber-600" />
                    <p className="text-xs font-semibold text-amber-800">Pending Approval</p>
                  </div>
                  <p className="text-xs text-amber-700">
                    Refund of ₹{(msg.pendingApproval as { amount?: number }).amount?.toLocaleString()} requires review
                  </p>
                </div>
              )}
              <p className={`text-[10px] mt-1.5 ${msg.role === 'user' ? 'text-white/50' : 'text-gray-400'}`}>
                {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3 msg-enter">
            <div className="flex-shrink-0 w-8 h-8 rounded-xl bg-gradient-to-br from-brand-100 to-brand-200 border border-brand-200 flex items-center justify-center shadow-sm">
              <Bot className="w-4 h-4 text-brand-600" />
            </div>
            <div className="bg-white border border-gray-100 rounded-2xl rounded-tl-md px-5 py-3.5 shadow-sm">
              <div className="flex items-center gap-1.5">
                <div className="w-2 h-2 bg-brand-400 rounded-full typing-dot" />
                <div className="w-2 h-2 bg-brand-400 rounded-full typing-dot" />
                <div className="w-2 h-2 bg-brand-400 rounded-full typing-dot" />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200/60 bg-white/80 backdrop-blur-xl p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-end gap-3 bg-gray-50 rounded-2xl border border-gray-200 p-2 focus-within:border-brand-300 focus-within:ring-2 focus-within:ring-brand-100 transition-all">
            <textarea rows={1} value={input} onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
              placeholder="Type your message..."
              className="flex-1 bg-transparent px-3 py-2.5 text-sm resize-none outline-none text-gray-800 placeholder-gray-400 max-h-32"
              disabled={loading} />
            <button onClick={sendMessage} disabled={loading || !input.trim()}
              className="flex-shrink-0 w-10 h-10 btn-gradient text-white rounded-xl flex items-center justify-center disabled:opacity-40 disabled:cursor-not-allowed disabled:transform-none transition-all">
              <Send className="w-4 h-4" />
            </button>
          </div>
          <p className="text-[10px] text-gray-400 mt-2 text-center">AI may make mistakes. Verify important information.</p>
        </div>
      </div>
    </div>
  );
}