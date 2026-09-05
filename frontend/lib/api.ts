/**
 * API client for TechKart backend.
 */
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ChatMessage {
  message: string;
  customer_id: string;
  thread_id?: string;
}

export interface ChatResponse {
  response: string;
  thread_id: string;
  customer_id: string;
  pending_approval?: Record<string, unknown> | null;
}

export interface Order {
  id: string;
  customer_id: string;
  status: string;
  total_amount: number;
  items: OrderItem[];
  payment: PaymentInfo | null;
  shipment: ShipmentInfo | null;
  created_at: string;
}

export interface OrderItem {
  product_id: string;
  product_name: string;
  category: string;
  brand: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface PaymentInfo {
  id: string;
  amount: number;
  status: string;
  payment_method: string;
  paid_at: string | null;
}

export interface ShipmentInfo {
  id: string;
  tracking_number: string;
  carrier: string;
  status: string;
  shipped_at: string | null;
  estimated_delivery: string | null;
  delivered_at: string | null;
  tracking_url: string | null;
}

export interface Approval {
  id: string;
  thread_id: string;
  customer_id: string;
  order_id: string | null;
  action_type: string;
  status: string;
  requested_amount: number | null;
  requested_reason: string | null;
  decision: string | null;
  decided_by: string | null;
  decided_at: string | null;
  decision_notes: string | null;
  ai_reasoning_summary: string | null;
  created_at: string;
}

export interface Customer {
  id: string;
  email: string;
  phone: string;
  first_name: string;
  last_name: string;
  full_name: string;
}

async function apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options?.headers },
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }
  return res.json();
}

export const api = {
  chat: (data: ChatMessage) =>
    apiCall<ChatResponse>('/api/v1/chat', { method: 'POST', body: JSON.stringify(data) }),

  getOrder: (id: string) => apiCall<Order>(`/api/v1/orders/${id}`),
  getOrderStatus: (id: string) => apiCall<{ order_id: string; status: string }>(`/api/v1/orders/${id}/status`),
  getCustomerOrders: (customerId: string) =>
    apiCall<{ orders: Order[]; count: number }>(`/api/v1/orders/customer/${customerId}`),

  getCustomer: (id: string) => apiCall<Customer>(`/api/v1/customers/${id}`),

  getPendingApprovals: () =>
    apiCall<{ approvals: Approval[]; count: number }>('/api/v1/approvals/pending'),
  getApproval: (threadId: string) => apiCall<Approval>(`/api/v1/approvals/${threadId}`),
  decideApproval: (threadId: string, decision: string, data?: { edited_amount?: number; notes?: string }) =>
    apiCall<{ success: boolean }>(`/api/v1/approvals/${threadId}/decide`, {
      method: 'POST',
      body: JSON.stringify({ decision, decided_by: 'SUPPORT_AGENT', ...data }),
    }),

  healthCheck: () => apiCall<{ status: string }>('/health'),
};