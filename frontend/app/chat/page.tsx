'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { ArrowLeft, Bot } from 'lucide-react';
import ChatWindow from '@/components/chat/ChatWindow';

function ChatContent() {
  const searchParams = useSearchParams();
  const customerId = searchParams.get('customer') || 'CUS1001';

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-brand-50/30 flex flex-col">
      {/* Header */}
      <header className="relative bg-hero-gradient text-white shadow-lg shadow-brand-900/10">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <a href="/"
              className="w-9 h-9 bg-white/15 hover:bg-white/25 rounded-lg flex items-center justify-center transition-colors">
              <ArrowLeft className="w-4 h-4" />
            </a>
            <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/20">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-base font-semibold tracking-tight">Support Chat</h1>
              <p className="text-xs text-white/60 font-mono">{customerId}</p>
            </div>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/20 backdrop-blur-sm rounded-full border border-emerald-400/20">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75 animate-ping" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
            </span>
            <span className="text-xs font-medium text-emerald-100">Online</span>
          </div>
        </div>
      </header>

      {/* Chat */}
      <div className="flex-1 max-w-4xl mx-auto w-full">
        <ChatWindow customerId={customerId} />
      </div>
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-brand-50/30 flex flex-col">
        <header className="relative bg-hero-gradient text-white shadow-lg shadow-brand-900/10">
          <div className="max-w-4xl mx-auto px-4 py-4 flex items-center gap-3">
            <a href="/" className="w-9 h-9 bg-white/15 hover:bg-white/25 rounded-lg flex items-center justify-center transition-colors">
              <ArrowLeft className="w-4 h-4" />
            </a>
            <h1 className="text-base font-semibold tracking-tight">Support Chat</h1>
          </div>
        </header>
        <div className="flex-1 flex items-center justify-center">
          <div className="w-8 h-8 border-3 border-brand-300 border-t-brand-600 rounded-full animate-spin" />
        </div>
      </div>
    }>
      <ChatContent />
    </Suspense>
  );
}