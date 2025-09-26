'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import apiClient from '@/lib/api';

interface Order {
  id: number;
  order_number: string;
  status: string;
  total: number;
  created_at: string;
  paid_at?: string;
  items: Array<{
    id: number;
    variant: {
      product: {
        name: string;
        slug: string;
        primary_image?: {
          image: string;
          alt_text: string;
        };
      };
    };
    quantity: number;
  }>;
}

export default function OrdersPage() {
  const { data: orders, isLoading, error } = useQuery<Order[]>({
    queryKey: ['orders'],
    queryFn: async () => {
      const response = await apiClient.get('/orders/');
      return response.data.results || response.data;
    },
  });

  const getStatusColor = (status: string) => {
    const colors = {
      draft: 'bg-gray-100 text-gray-800',
      awaiting_payment: 'bg-yellow-100 text-yellow-800',
      paid: 'bg-green-100 text-green-800',
      processing: 'bg-blue-100 text-blue-800',
      shipped: 'bg-purple-100 text-purple-800',
      delivered: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800',
      refunded: 'bg-gray-100 text-gray-800',
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
            <div className="space-y-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="bg-white rounded-lg shadow p-6">
                  <div className="flex justify-between items-start">
                    <div className="space-y-2">
                      <div className="h-4 bg-gray-200 rounded w-32"></div>
                      <div className="h-3 bg-gray-200 rounded w-24"></div>
                    </div>
                    <div className="h-6 bg-gray-200 rounded w-20"></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Error loading orders</h2>
          <p className="text-gray-600 mb-6">Please try again later.</p>
          <Link
            href="/"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
          >
            Go Home
          </Link>
        </div>
      </div>
    );
  }

  if (!orders || orders.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h2 className="mt-2 text-2xl font-bold text-gray-900">No orders yet</h2>
            <p className="mt-1 text-gray-500">Start shopping to see your orders here.</p>
            <div className="mt-6">
              <Link
                href="/products"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
              >
                Start Shopping
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Your Orders</h1>
          <p className="text-gray-600">Track and manage your orders</p>
        </div>

        <div className="space-y-6">
          {orders.map((order) => (
            <div key={order.id} className="bg-white rounded-lg shadow">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">
                      Order #{order.order_number}
                    </h3>
                    <p className="text-sm text-gray-500">
                      Placed on {new Date(order.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(order.status)}`}>
                      {order.status.replace('_', ' ').toUpperCase()}
                    </span>
                    <span className="text-lg font-medium text-gray-900">
                      ${order.total.toFixed(2)}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    {order.items.slice(0, 3).map((item, index) => (
                      <div key={item.id} className="flex-shrink-0 h-12 w-12">
                        {item.variant.product.primary_image ? (
                          <img
                            src={item.variant.product.primary_image.image}
                            alt={item.variant.product.primary_image.alt_text}
                            className="h-full w-full object-cover object-center rounded"
                          />
                        ) : (
                          <div className="h-full w-full bg-gray-200 rounded flex items-center justify-center">
                            <span className="text-gray-400 text-xs">No image</span>
                          </div>
                        )}
                      </div>
                    ))}
                    {order.items.length > 3 && (
                      <div className="flex-shrink-0 h-12 w-12 bg-gray-100 rounded flex items-center justify-center">
                        <span className="text-sm text-gray-500">+{order.items.length - 3}</span>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center space-x-4">
                    <Link
                      href={`/orders/${order.id}`}
                      className="text-indigo-600 hover:text-indigo-500 text-sm font-medium"
                    >
                      View Details
                    </Link>
                    {order.status === 'delivered' && (
                      <button className="text-indigo-600 hover:text-indigo-500 text-sm font-medium">
                        Reorder
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
