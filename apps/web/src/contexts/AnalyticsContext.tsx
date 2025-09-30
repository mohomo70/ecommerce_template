'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

interface AnalyticsSummary {
  total_revenue: number;
  total_orders: number;
  total_customers: number;
  total_products: number;
  average_order_value: number;
  conversion_rate: number;
  period: string;
}

interface TopProduct {
  product: {
    id: number;
    name: string;
    slug: string;
    short_description: string;
    category: {
      id: number;
      name: string;
    };
    primary_image: {
      image: string;
      alt_text: string;
    } | null;
    price_range: string;
    is_active: boolean;
    is_featured: boolean;
    created_at: string;
    variant_count: number;
  };
  revenue: number;
  orders: number;
  conversion_rate: number;
}

interface TopCategory {
  category: {
    id: number;
    name: string;
    slug: string;
    description: string;
    parent: number | null;
    is_active: boolean;
    created_at: string;
  };
  revenue: number;
  orders: number;
  products: number;
}

interface RevenueTrend {
  date: string;
  revenue: number;
  orders: number;
}

interface AnalyticsContextType {
  summary: AnalyticsSummary | null;
  topProducts: TopProduct[];
  topCategories: TopCategory[];
  revenueTrend: RevenueTrend[];
  loading: boolean;
  error: string | null;
  fetchSummary: (days?: number) => Promise<void>;
  fetchTopProducts: (days?: number, limit?: number) => Promise<void>;
  fetchTopCategories: (days?: number, limit?: number) => Promise<void>;
  fetchRevenueTrend: (days?: number) => Promise<void>;
  trackPageView: (url: string) => Promise<void>;
  trackSearch: (query: string, resultsCount: number) => Promise<void>;
  trackConversion: (eventType: string, data?: any) => Promise<void>;
}

const AnalyticsContext = createContext<AnalyticsContextType | undefined>(undefined);

export const useAnalytics = () => {
  const context = useContext(AnalyticsContext);
  if (!context) {
    throw new Error('useAnalytics must be used within an AnalyticsProvider');
  }
  return context;
};

export const AnalyticsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuth();
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [topProducts, setTopProducts] = useState<TopProduct[]>([]);
  const [topCategories, setTopCategories] = useState<TopCategory[]>([]);
  const [revenueTrend, setRevenueTrend] = useState<RevenueTrend[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiCall = async (endpoint: string, options: RequestInit = {}) => {
    const response = await fetch(`/api/analytics${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API call failed: ${response.statusText}`);
    }

    return response.json();
  };

  const fetchSummary = async (days: number = 30) => {
    try {
      setLoading(true);
      const data = await apiCall(`/summary/?days=${days}`);
      setSummary(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch analytics summary');
    } finally {
      setLoading(false);
    }
  };

  const fetchTopProducts = async (days: number = 30, limit: number = 10) => {
    try {
      setLoading(true);
      const data = await apiCall(`/top-products/?days=${days}&limit=${limit}`);
      setTopProducts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch top products');
    } finally {
      setLoading(false);
    }
  };

  const fetchTopCategories = async (days: number = 30, limit: number = 10) => {
    try {
      setLoading(true);
      const data = await apiCall(`/top-categories/?days=${days}&limit=${limit}`);
      setTopCategories(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch top categories');
    } finally {
      setLoading(false);
    }
  };

  const fetchRevenueTrend = async (days: number = 30) => {
    try {
      setLoading(true);
      const data = await apiCall(`/revenue-trend/?days=${days}`);
      setRevenueTrend(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch revenue trend');
    } finally {
      setLoading(false);
    }
  };

  const trackPageView = async (url: string) => {
    try {
      await apiCall('/track/page-view/', {
        method: 'POST',
        body: JSON.stringify({ url }),
      });
    } catch (err) {
      console.error('Failed to track page view:', err);
    }
  };

  const trackSearch = async (query: string, resultsCount: number) => {
    try {
      await apiCall('/track/search/', {
        method: 'POST',
        body: JSON.stringify({ query, results_count: resultsCount }),
      });
    } catch (err) {
      console.error('Failed to track search:', err);
    }
  };

  const trackConversion = async (eventType: string, data: any = {}) => {
    try {
      await apiCall('/track/conversion/', {
        method: 'POST',
        body: JSON.stringify({
          event_type: eventType,
          ...data,
        }),
      });
    } catch (err) {
      console.error('Failed to track conversion:', err);
    }
  };

  useEffect(() => {
    if (user && user.roles.includes('admin')) {
      fetchSummary();
      fetchTopProducts();
      fetchTopCategories();
      fetchRevenueTrend();
    }
  }, [user]);

  const value: AnalyticsContextType = {
    summary,
    topProducts,
    topCategories,
    revenueTrend,
    loading,
    error,
    fetchSummary,
    fetchTopProducts,
    fetchTopCategories,
    fetchRevenueTrend,
    trackPageView,
    trackSearch,
    trackConversion,
  };

  return (
    <AnalyticsContext.Provider value={value}>
      {children}
    </AnalyticsContext.Provider>
  );
};
