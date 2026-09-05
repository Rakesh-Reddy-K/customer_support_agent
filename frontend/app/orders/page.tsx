'use client';

import { useState } from 'react';
import { Package, Search, Truck, CreditCard, ArrowLeft, ShoppingCart } from 'lucide-react';
import { api, Order } from '@/lib/api';

export default function OrdersPage() {
  const [customerId, setCustomerId] = useState('CUS1001');
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searched, setSearched] = useState(false);

  const fetchOrders = async () => {
    setLoading(true);
    setError('');
    setSearched(true);
    try {
      const res = await api.getCustomerOrders(customerId);
      setOrders(res.orders);
    } catch {
      setError('Failed to fetch orders');
    } finally {
      setLoading(false);
    }
  };

  const statusColor = (s: string) => {
    const colors: Record<string, string> = {
      DELIVERED: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      SHIPPED: 'bg-blue-50 text-blue-700 border-blue-200',
      PROCESSING: 'bg-amber-50 text-amber-700 border-amber-200',
      CONFIRMED: 'bg-indigo-50 text-indigo-700 border-indigo-200',
      PENDING: 'bg-gray-50 text-gray-600 border-gray-200',
      CANCELLED: 'bg-red-50 text-red-700 border-red-200',
      REFUNDED: 'bg-orange-50 text-orange-700 border-orange-200',
    };
    return colors[s] || 'bg-gray-50 text-gray-600 border-gray-200';
  };

  const statusDot = (s: string) => {
    const d: Record<string, string> = {
      DELIVERED: 'bg-emerald-500', SHIPPED: 'bg-blue-500', PROCESSING: 'bg-amber-500',
      CONFIRMED: 'bg-indigo-500', PENDING: 'bg-gray-400', CANCELLED: 'bg-red-500', REFUNDED: 'bg-orange-500',
    };
    return d[s] || 'bg-gray-400';
  };

  const totalSpent = orders.reduce((sum, o) => sum + o.total_amount, 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-emerald-50/20">
      <header className="relative bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 text-white shadow-lg">
        <div className="max-w-6xl mx-auto px-6 py-5 flex items-center gap-4">
          <a href="/" className="w-9 h-9 bg-white/10 hover:bg-white/20 rounded-lg flex items-center justify-center transition-colors">
            <ArrowLeft className="w-4 h-4" />
          </a>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center shadow-lg">
              <Package className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold tracking-tight">Orders</h1>
              <p className="text-xs text-white/50">Track &amp; manage customer orders</p>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Search Bar */}
        <div className="glass-strong rounded-2xl p-4 shadow-lg shadow-gray-200/40 mb-8 animate-slide-up">
          <div className="flex items-center gap-3">
            <div className="flex-1 flex items-center gap-3 bg-gray-50 rounded-xl px-4 py-3 border border-gray-200 focus-within:border-emerald-300 focus-within:ring-2 focus-within:ring-emerald-100 transition-all">
              <Search className="w-4 h-4 text-gray-400" />
              <input type="text" value={customerId} onChange={(e) => setCustomerId(e.target.value)}
                placeholder="Customer ID (e.g. CUS1001)"
                className="flex-1 bg-transparent text-sm outline-none text-gray-800 placeholder-gray-400 font-mono tracking-wide" />
            </div>
            <button onClick={fetchOrders} disabled={loading}
              className="flex items-center gap-2 px-6 py-3 btn-gradient text-white rounded-xl font-medium text-sm disabled:opacity-50 whitespace-nowrap">
              {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Search className="w-4 h-4" />}
              Search
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-6 text-sm animate-slide-down">{error}</div>
        )}

        {/* Stats */}
        {searched && !loading && (
          <div className="grid grid-cols-3 gap-4 mb-8 animate-slide-up">
            {[
              { label: 'Total Orders', value: orders.length, icon: ShoppingCart, color: 'from-indigo-500 to-purple-600' },
              { label: 'Total Spent', value: `₹${totalSpent.toLocaleString()}`, icon: CreditCard, color: 'from-emerald-500 to-teal-600' },
              { label: 'Delivered', value: orders.filter(o => o.status === 'DELIVERED').length, icon: Truck, color: 'from-blue-500 to-indigo-600' },
            ].map((stat) => (
              <div key={stat.label} className="glass-strong rounded-2xl p-4 shadow-md shadow-gray-200/30">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 bg-gradient-to-br ${stat.color} rounded-xl flex items-center justify-center shadow-md`}>
                    <stat.icon className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 font-medium">{stat.label}</p>
                    <p className="text-lg font-bold text-gray-900">{stat.value}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Loading skeletons */}
        {loading && (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="glass-strong rounded-2xl p-5 space-y-3">
                <div className="skeleton h-5 w-32" />
                <div className="skeleton h-4 w-48" />
                <div className="skeleton h-3 w-64" />
              </div>
            ))}
          </div>
        )}

        {/* Order Cards */}
        {!loading && orders.length > 0 && (
          <div className="space-y-4">
            {orders.map((order, idx) => (
              <div key={order.id}
                className="group glass-strong rounded-2xl overflow-hidden shadow-md shadow-gray-200/30 card-hover animate-slide-up"
                style={{ animationDelay: `${idx * 60}ms` }}>
                <div className="flex">
                  <div className={`w-1.5 flex-shrink-0 ${statusDot(order.status)}`} />
                  <div className="flex-1 p-5">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="font-bold text-gray-900 text-base">{order.id}</h3>
                        <p className="text-sm text-gray-500 mt-0.5">
                          {order.items?.length} item{order.items?.length !== 1 ? 's' : ''} &middot; Created {new Date(order.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-lg font-bold text-gray-900">₹{order.total_amount.toLocaleString()}</span>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${statusColor(order.status)}`}>
                          {order.status}
                        </span>
                      </div>
                    </div>
                    {order.items?.length > 0 && (
                      <div className="bg-gray-50 rounded-xl p-3 mb-3">
                        {order.items.map((item, i) => (
                          <div key={i} className="flex items-center justify-between py-1.5">
                            <span className="text-sm text-gray-700">
                              {item.product_name} <span className="text-gray-400">&middot;</span> <span className="text-gray-500">{item.brand}</span>
                              <span className="text-gray-400"> &times; {item.quantity}</span>
                            </span>
                            <span className="text-sm font-medium text-gray-900">₹{item.total_price.toLocaleString()}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    {order.shipment && (
                      <div className="flex items-center gap-2 text-xs text-gray-500 bg-blue-50/50 rounded-lg px-3 py-2 border border-blue-100/50">
                        <Truck className="w-3.5 h-3.5 text-blue-500" />
                        <span className="font-medium">{order.shipment.carrier}</span>
                        <span>&middot;</span>
                        <span className="font-mono">{order.shipment.tracking_number}</span>
                        <span>&middot;</span>
                        <span className={`font-medium ${order.shipment.status === 'DELIVERED' ? 'text-emerald-600' : 'text-blue-600'}`}>
                          {order.shipment.status}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {!loading && searched && orders.length === 0 && (
          <div className="glass-strong rounded-2xl p-12 text-center animate-fade-in">
            <Package className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 font-medium">No orders found</p>
            <p className="text-sm text-gray-400 mt-1">Try a different customer ID</p>
          </div>
        )}

        {!searched && (
          <div className="glass-strong rounded-2xl p-12 text-center animate-fade-in">
            <Search className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 font-medium">Search for a customer</p>
            <p className="text-sm text-gray-400 mt-1">Enter a customer ID and click Search to view their orders</p>
          </div>
        )}
      </div>
    </div>
  );
}