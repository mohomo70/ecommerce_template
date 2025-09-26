'use client';

import { useState, useEffect } from 'react';
import { usePayment } from '@/contexts/PaymentContext';
import { useRouter } from 'next/navigation';

interface PaymentFormProps {
  orderId: number;
  orderNumber: string;
  total: number;
  onSuccess?: (orderId: number, orderNumber: string) => void;
  onError?: (error: string) => void;
}

export default function PaymentForm({ orderId, orderNumber, total, onSuccess, onError }: PaymentFormProps) {
  const { createPaymentIntent, confirmPayment, isCreatingIntent, isConfirmingPayment } = usePayment();
  const router = useRouter();
  const [clientSecret, setClientSecret] = useState<string>('');
  const [paymentIntentId, setPaymentIntentId] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    // Create payment intent when component mounts
    const createIntent = async () => {
      try {
        const result = await createPaymentIntent(orderId);
        setClientSecret(result.client_secret);
        setPaymentIntentId(result.payment_intent_id);
      } catch (err: any) {
        setError(err.response?.data?.error || 'Failed to create payment intent');
        onError?.(error);
      }
    };

    createIntent();
  }, [orderId, createPaymentIntent, onError, error]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsProcessing(true);
    setError('');

    try {
      const result = await confirmPayment(paymentIntentId);
      
      if (result.status === 'succeeded') {
        onSuccess?.(result.order_id, result.order_number);
        router.push(`/orders/${result.order_id}`);
      } else {
        setError('Payment failed. Please try again.');
        onError?.('Payment failed');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || 'Payment failed. Please try again.';
      setError(errorMessage);
      onError?.(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  if (isCreatingIntent) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        <span className="ml-2 text-gray-600">Setting up payment...</span>
      </div>
    );
  }

  if (!clientSecret) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 mb-4">Failed to initialize payment</p>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Payment Details</h2>
        
        <div className="mb-4 p-4 bg-gray-50 rounded-md">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Order #{orderNumber}</span>
            <span className="text-lg font-semibold text-gray-900">${total.toFixed(2)}</span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="card-element" className="block text-sm font-medium text-gray-700 mb-2">
              Card Information
            </label>
            <div className="p-3 border border-gray-300 rounded-md">
              <div className="text-sm text-gray-500">
                This is a demo payment form. In a real implementation, you would integrate with Stripe Elements here.
              </div>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <div className="flex space-x-4">
            <button
              type="button"
              onClick={() => router.back()}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Back
            </button>
            <button
              type="submit"
              disabled={isProcessing || isConfirmingPayment}
              className="flex-1 px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isProcessing || isConfirmingPayment ? 'Processing...' : `Pay $${total.toFixed(2)}`}
            </button>
          </div>
        </form>

        <div className="mt-4 text-xs text-gray-500">
          <p>This is a demo payment form. No real payment will be processed.</p>
          <p>In production, this would integrate with Stripe Elements for secure card collection.</p>
        </div>
      </div>
    </div>
  );
}
