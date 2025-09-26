'use client';

import { useQuery } from '@tanstack/react-query';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import apiClient from '@/lib/api';

interface OrderItem {
  id: number;
  variant: {
    id: number;
    sku: string;
    name: string;
    price: string;
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
  line_total: string;
}

interface Order {
  id: number;
  order_number: string;
  status: string;
  email: string;
  billing_first_name: string;
  billing_last_name: string;
  billing_company?: string;
  billing_address_1: string;
  billing_address_2?: string;
  billing_city: string;
  billing_state: string;
  billing_postal_code: string;
  billing_country: string;
  billing_phone?: string;
  shipping_first_name: string;
  shipping_last_name: string;
  shipping_company?: string;
  shipping_address_1: string;
  shipping_address_2?: string;
  shipping_city: string;
  shipping_state: string;
  shipping_postal_code: string;
  shipping_country: string;
  shipping_phone?: string;
  subtotal: number;
  tax_amount: number;
  shipping_amount: number;
  total: number;
  payment_status: string;
  created_at: string;
  paid_at?: string;
  items: OrderItem[];
}

export default function OrderDetailPage() {
  const params = useParams();
  const orderId = params.id;

  const { data: order, isLoading, error } = useQuery<Order>({
    queryKey: ['order', orderId],
    queryFn: async () => {
      const response = await apiClient.get(`/orders/${orderId}/`);
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Order Not Found</h2>
          <p className="text-gray-600 mb-6">The order you're looking for doesn't exist or you don't have permission to view it.</p>
          <Link
            href="/orders"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
          >
            View All Orders
          </Link>
        </div>
      </div>
    );
  }

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

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Order Confirmation</h1>
                <p className="text-lg text-gray-600">Order #{order.order_number}</p>
              </div>
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(order.status)}`}>
                {order.status.replace('_', ' ').toUpperCase()}
              </span>
            </div>
            <p className="text-sm text-gray-500 mt-2">
              Placed on {new Date(order.created_at).toLocaleDateString()} at {new Date(order.created_at).toLocaleTimeString()}
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Order Items */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow p-6 mb-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Order Items</h2>
                <div className="space-y-4">
                  {order.items.map((item) => (
                    <div key={item.id} className="flex items-center space-x-4 py-4 border-b border-gray-200 last:border-b-0">
                      <div className="flex-shrink-0 h-16 w-16">
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
                      <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-medium text-gray-900">
                          <Link
                            href={`/products/${item.variant.product.slug}`}
                            className="hover:text-indigo-600"
                          >
                            {item.variant.product.name}
                          </Link>
                        </h3>
                        <p className="text-sm text-gray-500">{item.variant.name}</p>
                        <p className="text-sm text-gray-500">SKU: {item.variant.sku}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-900">
                          ${item.price} × {item.quantity}
                        </p>
                        <p className="text-sm font-medium text-gray-900">
                          ${item.line_total}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Addresses */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Billing Address</h3>
                  <div className="text-sm text-gray-600">
                    <p className="font-medium">{order.billing_first_name} {order.billing_last_name}</p>
                    {order.billing_company && <p>{order.billing_company}</p>}
                    <p>{order.billing_address_1}</p>
                    {order.billing_address_2 && <p>{order.billing_address_2}</p>}
                    <p>{order.billing_city}, {order.billing_state} {order.billing_postal_code}</p>
                    <p>{order.billing_country}</p>
                    {order.billing_phone && <p>{order.billing_phone}</p>}
                  </div>
                </div>

                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Shipping Address</h3>
                  <div className="text-sm text-gray-600">
                    <p className="font-medium">{order.shipping_first_name} {order.shipping_last_name}</p>
                    {order.shipping_company && <p>{order.shipping_company}</p>}
                    <p>{order.shipping_address_1}</p>
                    {order.shipping_address_2 && <p>{order.shipping_address_2}</p>}
                    <p>{order.shipping_city}, {order.shipping_state} {order.shipping_postal_code}</p>
                    <p>{order.shipping_country}</p>
                    {order.shipping_phone && <p>{order.shipping_phone}</p>}
                  </div>
                </div>
              </div>
            </div>

            {/* Order Summary */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow p-6 sticky top-8">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Order Summary</h2>
                
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Subtotal</span>
                    <span className="text-gray-900">${order.subtotal.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Tax</span>
                    <span className="text-gray-900">${order.tax_amount.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Shipping</span>
                    <span className="text-gray-900">${order.shipping_amount.toFixed(2)}</span>
                  </div>
                  <div className="border-t border-gray-200 pt-3">
                    <div className="flex justify-between text-lg font-medium">
                      <span>Total</span>
                      <span>${order.total.toFixed(2)}</span>
                    </div>
                  </div>
                </div>

                <div className="mt-6 space-y-3">
                  <Link
                    href="/products"
                    className="w-full flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
                  >
                    Continue Shopping
                  </Link>
                  <Link
                    href="/orders"
                    className="w-full flex justify-center items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                  >
                    View All Orders
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
