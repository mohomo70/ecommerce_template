'use client';

import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';

export default function Home() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
            Welcome to Ecommerce
          </h1>
          <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
            Your one-stop shop for all your needs. Browse our products and find exactly what you're looking for.
          </p>
          
          {user ? (
            <div className="mt-8">
              <p className="text-lg text-gray-600">
                Welcome back, {user.first_name || user.email}!
              </p>
              <div className="mt-5 flex justify-center space-x-4">
                <Link
                  href="/products"
                  className="bg-indigo-600 text-white px-6 py-3 rounded-md text-lg font-medium hover:bg-indigo-700"
                >
                  Browse Products
                </Link>
                <Link
                  href="/account"
                  className="bg-white text-indigo-600 px-6 py-3 rounded-md text-lg font-medium border border-indigo-600 hover:bg-indigo-50"
                >
                  My Account
                </Link>
              </div>
            </div>
          ) : (
            <div className="mt-8">
              <div className="flex justify-center space-x-4">
                <Link
                  href="/signup"
                  className="bg-indigo-600 text-white px-6 py-3 rounded-md text-lg font-medium hover:bg-indigo-700"
                >
                  Get Started
                </Link>
                <Link
                  href="/login"
                  className="bg-white text-indigo-600 px-6 py-3 rounded-md text-lg font-medium border border-indigo-600 hover:bg-indigo-50"
                >
                  Sign In
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
