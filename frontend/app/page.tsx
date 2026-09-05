'use client';

import { useState } from 'react';
import Link from 'next/link';
import { MessageSquare, Package, ShieldCheck, ArrowRight, Bot, Sparkles } from 'lucide-react';

export default function Home() {
  const [customerId, setCustomerId] = useState('CUS1001');

  return (
    <div className="min-h-screen">
      {/* Hero Header */}
      <header className="relative bg-hero-gradient text-white overflow-hidden">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-white/5 rounded-full blur-3xl" />
        <div className="absolute -bottom-32 -left-16 w-80 h-80 bg-purple-400/10 rounded-full blur-3xl" />
        <div className="relative max-w-7xl mx-auto px-6 py-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/20">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">TechKart</h1>
              <p className="text-xs text-white/60 font-medium">AI Customer Support</p>
            </div>
          </div>
          <nav className="flex items-center gap-1">
            {[
              { href: '/chat', label: 'Chat' },
              { href: '/orders', label: 'Orders' },
              { href: '/approvals', label: 'Approvals' },
            ].map((item) => (
              <Link key={item.href} href={item.href}
                className="px-4 py-2 text-sm font-medium text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-all">
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative bg-hero-gradient text-white pb-32 pt-16 px-6">
        <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'radial-gradient(circle, white 1px, transparent 1px)', backgroundSize: '24px 24px' }} />
        <div className="relative max-w-3xl mx-auto text-center animate-fade-in">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-white/10 backdrop-blur-sm rounded-full border border-white/20 text-sm font-medium mb-8">
            <Sparkles className="w-4 h-4 text-amber-300" />
            Powered by LangGraph + Ollama
          </div>
          <h2 className="text-5xl font-bold tracking-tight mb-6 leading-tight">
            Welcome to<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-200 via-white to-purple-200">
              TechKart Support
            </span>
          </h2>
          <p className="text-lg text-white/70 max-w-xl mx-auto mb-12 leading-relaxed">
            Our AI agent handles orders, shipments, refunds, and policy questions —
            with human-in-the-loop approvals for sensitive actions.
          </p>
          {/* Customer Selector */}
          <div className="max-w-lg mx-auto animate-slide-up">
            <div className="bg-white/10 backdrop-blur-xl rounded-2xl border border-white/20 p-2">
              <div className="flex items-center gap-2">
                <div className="flex-1 flex items-center gap-3 bg-white/10 rounded-xl px-4 py-3">
                  <span className="text-white/50 text-sm font-medium whitespace-nowrap">Customer</span>
                  <input type="text" value={customerId} onChange={(e) => setCustomerId(e.target.value)}
                    className="flex-1 bg-transparent text-white placeholder-white/40 text-sm outline-none font-mono tracking-wide"
                    placeholder="CUS1001" />
                </div>
                <Link href={`/chat?customer=${customerId}`}
                  className="flex items-center gap-2 px-6 py-3 bg-white text-brand-700 rounded-xl hover:bg-brand-50 transition-all font-semibold text-sm shadow-lg shadow-black/10 whitespace-nowrap">
                  Start Chat
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Actions */}
      <main className="max-w-5xl mx-auto px-6 -mt-16 relative z-10 pb-20">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {[
            { href: `/chat?customer=${customerId}`, icon: MessageSquare, iconBg: 'bg-gradient-to-br from-blue-500 to-indigo-600', title: 'Chat Support', desc: 'Talk to our AI agent for instant help with orders, refunds, and more.' },
            { href: '/orders', icon: Package, iconBg: 'bg-gradient-to-br from-emerald-500 to-teal-600', title: 'Track Orders', desc: 'Check order status, tracking info, and delivery details.' },
            { href: '/approvals', icon: ShieldCheck, iconBg: 'bg-gradient-to-br from-amber-500 to-orange-600', title: 'Approvals', desc: 'Review and approve pending refund requests and actions.' },
          ].map((card, i) => (
            <Link key={card.title} href={card.href}
              className="group glass-strong rounded-2xl p-6 shadow-lg shadow-gray-200/60 card-hover animate-slide-up"
              style={{ animationDelay: `${i * 80}ms` }}>
              <div className={`w-12 h-12 ${card.iconBg} rounded-xl flex items-center justify-center mb-5 shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                <card.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-brand-600 transition-colors">{card.title}</h3>
              <p className="text-sm text-gray-500 leading-relaxed">{card.desc}</p>
              <div className="mt-4 flex items-center gap-1 text-sm font-medium text-brand-600 opacity-0 group-hover:opacity-100 transition-opacity">
                Get started <ArrowRight className="w-4 h-4" />
              </div>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}