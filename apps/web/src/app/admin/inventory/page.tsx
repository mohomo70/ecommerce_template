'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';

interface StockLevel {
  variant_id: number;
  sku: string;
  product_name: string;
  current_stock: number;
  threshold: number;
  status: 'in_stock' | 'low_stock' | 'out_of_stock';
  last_movement: string | null;
}

interface LowStockAlert {
  id: number;
  variant: {
    sku: string;
    product: {
      name: string;
    };
  };
  threshold: number;
  current_stock: number;
  status: string;
  created_at: string;
}

export default function InventoryPage() {
  const [activeTab, setActiveTab] = useState('overview');

  // Fetch stock levels
  const { data: stockLevels, isLoading: isLoadingStock } = useQuery<StockLevel[]>({
    queryKey: ['stock-levels'],
    queryFn: async () => {
      const response = await apiClient.get('/inventory/levels/');
      return response.data;
    },
  });

  // Fetch low stock alerts
  const { data: lowStockAlerts, isLoading: isLoadingAlerts } = useQuery<LowStockAlert[]>({
    queryKey: ['low-stock-alerts'],
    queryFn: async () => {
      const response = await apiClient.get('/inventory/alerts/');
      return response.data;
    },
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'in_stock':
        return 'bg-green-100 text-green-800';
      case 'low_stock':
        return 'bg-yellow-100 text-yellow-800';
      case 'out_of_stock':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'in_stock':
        return 'In Stock';
      case 'low_stock':
        return 'Low Stock';
      case 'out_of_stock':
        return 'Out of Stock';
      default:
        return status;
    }
  };

  if (isLoadingStock || isLoadingAlerts) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Inventory Management</h1>
          <p className="text-gray-600">Track and manage your inventory levels</p>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', name: 'Overview' },
              { id: 'stock-levels', name: 'Stock Levels' },
              { id: 'alerts', name: 'Low Stock Alerts' },
              { id: 'adjustments', name: 'Stock Adjustments' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-100 rounded-md flex items-center justify-center">
                    <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">In Stock</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {stockLevels?.filter(item => item.status === 'in_stock').length || 0}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-yellow-100 rounded-md flex items-center justify-center">
                    <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Low Stock</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {stockLevels?.filter(item => item.status === 'low_stock').length || 0}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-red-100 rounded-md flex items-center justify-center">
                    <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Out of Stock</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {stockLevels?.filter(item => item.status === 'out_of_stock').length || 0}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-100 rounded-md flex items-center justify-center">
                    <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Total Items</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {stockLevels?.length || 0}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Stock Levels Tab */}
        {activeTab === 'stock-levels' && (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <div className="px-4 py-5 sm:px-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">Stock Levels</h3>
              <p className="mt-1 max-w-2xl text-sm text-gray-500">
                Current stock levels for all tracked products
              </p>
            </div>
            <ul className="divide-y divide-gray-200">
              {stockLevels?.map((item) => (
                <li key={item.variant_id} className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                          {getStatusText(item.status)}
                        </span>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">{item.product_name}</div>
                        <div className="text-sm text-gray-500">SKU: {item.sku}</div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-sm text-gray-500">
                        <span className="font-medium">{item.current_stock}</span> / {item.threshold}
                      </div>
                      <div className="text-sm text-gray-500">
                        {item.last_movement ? new Date(item.last_movement).toLocaleDateString() : 'Never'}
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Low Stock Alerts Tab */}
        {activeTab === 'alerts' && (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <div className="px-4 py-5 sm:px-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">Low Stock Alerts</h3>
              <p className="mt-1 max-w-2xl text-sm text-gray-500">
                Products that need restocking
              </p>
            </div>
            <ul className="divide-y divide-gray-200">
              {lowStockAlerts?.map((alert) => (
                <li key={alert.id} className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          Low Stock
                        </span>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">{alert.variant.product.name}</div>
                        <div className="text-sm text-gray-500">SKU: {alert.variant.sku}</div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-sm text-gray-500">
                        <span className="font-medium text-red-600">{alert.current_stock}</span> / {alert.threshold}
                      </div>
                      <div className="text-sm text-gray-500">
                        {new Date(alert.created_at).toLocaleDateString()}
                      </div>
                      <button className="text-indigo-600 hover:text-indigo-500 text-sm font-medium">
                        Acknowledge
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Stock Adjustments Tab */}
        {activeTab === 'adjustments' && (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <div className="px-4 py-5 sm:px-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">Stock Adjustments</h3>
              <p className="mt-1 max-w-2xl text-sm text-gray-500">
                Recent stock adjustments and movements
              </p>
            </div>
            <div className="px-4 py-5 sm:px-6">
              <p className="text-gray-500">Stock adjustments functionality would be implemented here.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
