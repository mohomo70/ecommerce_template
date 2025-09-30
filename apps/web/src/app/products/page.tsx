'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import Image from 'next/image';
import apiClient from '@/lib/api';

interface Product {
  id: number;
  name: string;
  slug: string;
  short_description: string;
  category: {
    id: number;
    name: string;
    slug: string;
  };
  primary_image?: {
    image: string;
    alt_text: string;
  };
  price_range: string;
  is_featured: boolean;
  variant_count: number;
}

interface Category {
  id: number;
  name: string;
  slug: string;
}

interface ProductsResponse {
  results: Product[];
  count: number;
  next: string | null;
  previous: string | null;
}

function ProductsPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [filters, setFilters] = useState({
    search: searchParams.get('search') || '',
    category: searchParams.get('category') || '',
    min_price: searchParams.get('min_price') || '',
    max_price: searchParams.get('max_price') || '',
    is_featured: searchParams.get('featured') === 'true',
    in_stock: searchParams.get('in_stock') === 'true',
    ordering: searchParams.get('ordering') || '-created_at',
  });

  // Fetch categories
  const { data: categories = [] } = useQuery<Category[]>({
    queryKey: ['categories'],
    queryFn: async () => {
      const response = await apiClient.get('/categories/');
      return response.data;
    },
  });

  // Fetch products
  const { data: productsData, isLoading, error } = useQuery<ProductsResponse>({
    queryKey: ['products', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value.toString());
      });
      
      const response = await apiClient.get(`/products/?${params.toString()}`);
      return response.data;
    },
  });

  // Update URL when filters change
  useEffect(() => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.set(key, value.toString());
    });
    
    const newUrl = params.toString() ? `?${params.toString()}` : '';
    router.replace(`/products${newUrl}`, { scroll: false });
  }, [filters, router]);

  const handleFilterChange = (key: string, value: string | boolean) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      category: '',
      min_price: '',
      max_price: '',
      is_featured: false,
      in_stock: false,
      ordering: '-created_at',
    });
  };

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Error loading products</h2>
          <p className="text-gray-600">Please try again later.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filters Sidebar */}
          <div className="lg:w-64 flex-shrink-0">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Filters</h3>
                <button
                  onClick={clearFilters}
                  className="text-sm text-indigo-600 hover:text-indigo-500"
                >
                  Clear all
                </button>
              </div>

              {/* Search */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Search
                </label>
                <input
                  type="text"
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Search products..."
                />
              </div>

              {/* Category Filter */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category
                </label>
                <select
                  value={filters.category}
                  onChange={(e) => handleFilterChange('category', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="">All Categories</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.slug}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Price Range */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Price Range
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="number"
                    value={filters.min_price}
                    onChange={(e) => handleFilterChange('min_price', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="Min"
                  />
                  <input
                    type="number"
                    value={filters.max_price}
                    onChange={(e) => handleFilterChange('max_price', e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="Max"
                  />
                </div>
              </div>

              {/* Checkboxes */}
              <div className="space-y-3">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.is_featured}
                    onChange={(e) => handleFilterChange('is_featured', e.target.checked)}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Featured only</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.in_stock}
                    onChange={(e) => handleFilterChange('in_stock', e.target.checked)}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">In stock only</span>
                </label>
              </div>
            </div>
          </div>

          {/* Products Grid */}
          <div className="flex-1">
            <div className="flex items-center justify-between mb-6">
              <h1 className="text-2xl font-bold text-gray-900">
                Products {productsData && `(${productsData.count})`}
              </h1>
              
              {/* Sort */}
              <select
                value={filters.ordering}
                onChange={(e) => handleFilterChange('ordering', e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="-created_at">Newest first</option>
                <option value="created_at">Oldest first</option>
                <option value="name">Name A-Z</option>
                <option value="-name">Name Z-A</option>
                <option value="price_range">Price Low-High</option>
                <option value="-price_range">Price High-Low</option>
              </select>
            </div>

            {isLoading ? (
              <ProductSkeleton />
            ) : productsData?.results.length === 0 ? (
              <EmptyState />
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {productsData?.results.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            )}

            {/* Pagination would go here */}
          </div>
        </div>
      </div>
    </div>
  );
}

function ProductCard({ product }: { product: Product }) {
  return (
    <Link href={`/products/${product.slug}`} className="group">
      <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow duration-200">
        <div className="aspect-w-1 aspect-h-1 w-full overflow-hidden rounded-t-lg bg-gray-200">
          {product.primary_image ? (
            <Image
              src={product.primary_image.image}
              alt={product.primary_image.alt_text}
              width={300}
              height={300}
              className="h-full w-full object-cover object-center group-hover:opacity-75"
            />
          ) : (
            <div className="h-full w-full bg-gray-200 flex items-center justify-center">
              <span className="text-gray-400">No image</span>
            </div>
          )}
        </div>
        <div className="p-4">
          <h3 className="text-sm font-medium text-gray-900 group-hover:text-indigo-600">
            {product.name}
          </h3>
          <p className="mt-1 text-sm text-gray-500">{product.category.name}</p>
          <p className="mt-1 text-sm text-gray-600 line-clamp-2">
            {product.short_description}
          </p>
          <div className="mt-2 flex items-center justify-between">
            <p className="text-lg font-semibold text-gray-900">
              {product.price_range}
            </p>
            {product.is_featured && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                Featured
              </span>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}

function ProductSkeleton() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {Array.from({ length: 8 }).map((_, i) => (
        <div key={i} className="bg-white rounded-lg shadow animate-pulse">
          <div className="h-48 bg-gray-200 rounded-t-lg"></div>
          <div className="p-4">
            <div className="h-4 bg-gray-200 rounded mb-2"></div>
            <div className="h-3 bg-gray-200 rounded mb-2 w-3/4"></div>
            <div className="h-3 bg-gray-200 rounded mb-4 w-1/2"></div>
            <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          </div>
        </div>
      ))}
    </div>
  );
}

function EmptyState() {
  return (
    <div className="text-center py-12">
      <div className="mx-auto h-24 w-24 text-gray-400">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
        </svg>
      </div>
      <h3 className="mt-2 text-sm font-medium text-gray-900">No products found</h3>
      <p className="mt-1 text-sm text-gray-500">
        Try adjusting your search or filter criteria.
      </p>
    </div>
  );
}

export default function ProductsPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ProductsPageContent />
    </Suspense>
  );
}
