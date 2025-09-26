'use client';

import React, { createContext, useContext, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import apiClient from '@/lib/api';

interface PaymentContextType {
  createPaymentIntent: (orderId: number) => Promise<{ client_secret: string; payment_intent_id: string }>;
  confirmPayment: (paymentIntentId: string) => Promise<{ status: string; order_id: number; order_number: string }>;
  isCreatingIntent: boolean;
  isConfirmingPayment: boolean;
}

const PaymentContext = createContext<PaymentContextType | undefined>(undefined);

export function PaymentProvider({ children }: { children: React.ReactNode }) {
  // Create payment intent mutation
  const createIntentMutation = useMutation({
    mutationFn: async (orderId: number) => {
      const response = await apiClient.post('/payments/intent/create/', {
        order_id: orderId,
      });
      return response.data;
    },
  });

  // Confirm payment mutation
  const confirmPaymentMutation = useMutation({
    mutationFn: async (paymentIntentId: string) => {
      const response = await apiClient.post('/payments/intent/confirm/', {
        payment_intent_id: paymentIntentId,
      });
      return response.data;
    },
  });

  const createPaymentIntent = async (orderId: number) => {
    return await createIntentMutation.mutateAsync(orderId);
  };

  const confirmPayment = async (paymentIntentId: string) => {
    return await confirmPaymentMutation.mutateAsync(paymentIntentId);
  };

  const value = {
    createPaymentIntent,
    confirmPayment,
    isCreatingIntent: createIntentMutation.isPending,
    isConfirmingPayment: confirmPaymentMutation.isPending,
  };

  return <PaymentContext.Provider value={value}>{children}</PaymentContext.Provider>;
}

export function usePayment() {
  const context = useContext(PaymentContext);
  if (context === undefined) {
    throw new Error('usePayment must be used within a PaymentProvider');
  }
  return context;
}
