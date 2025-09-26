'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';

interface Address {
  first_name: string;
  last_name: string;
  company?: string;
  address_1: string;
  address_2?: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  phone?: string;
}

interface OrderDraft {
  id: number;
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
}

interface CheckoutContextType {
  currentStep: number;
  setCurrentStep: (step: number) => void;
  draft: OrderDraft | null;
  isLoading: boolean;
  createDraft: () => Promise<void>;
  updateBillingAddress: (address: Address) => Promise<void>;
  updateShippingAddress: (address: Address) => Promise<void>;
  finalizeOrder: () => Promise<{ order_id: number; order_number: string }>;
  isCreatingDraft: boolean;
  isUpdatingDraft: boolean;
  isFinalizing: boolean;
}

const CheckoutContext = createContext<CheckoutContextType | undefined>(undefined);

export function CheckoutProvider({ children }: { children: React.ReactNode }) {
  const [currentStep, setCurrentStep] = useState(1);
  const queryClient = useQueryClient();

  // Fetch order draft
  const { data: draft, isLoading } = useQuery<OrderDraft>({
    queryKey: ['order-draft'],
    queryFn: async () => {
      const response = await apiClient.get('/orders/draft/');
      return response.data;
    },
    retry: false,
  });

  // Create draft mutation
  const createDraftMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post('/orders/draft/create/');
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.setQueryData(['order-draft'], data);
    },
  });

  // Update draft mutation
  const updateDraftMutation = useMutation({
    mutationFn: async ({ draftId, data }: { draftId: number; data: any }) => {
      const response = await apiClient.patch(`/orders/draft/${draftId}/`, data);
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.setQueryData(['order-draft'], data);
    },
  });

  // Finalize order mutation
  const finalizeOrderMutation = useMutation({
    mutationFn: async () => {
      if (!draft) throw new Error('No draft available');
      const response = await apiClient.post('/orders/finalize/', {
        draft_id: draft.id,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
      queryClient.invalidateQueries({ queryKey: ['order-draft'] });
    },
  });

  const createDraft = async () => {
    await createDraftMutation.mutateAsync();
  };

  const updateBillingAddress = async (address: Address) => {
    if (!draft) throw new Error('No draft available');
    await updateDraftMutation.mutateAsync({
      draftId: draft.id,
      data: {
        email: draft.email,
        billing_first_name: address.first_name,
        billing_last_name: address.last_name,
        billing_company: address.company,
        billing_address_1: address.address_1,
        billing_address_2: address.address_2,
        billing_city: address.city,
        billing_state: address.state,
        billing_postal_code: address.postal_code,
        billing_country: address.country,
        billing_phone: address.phone,
      },
    });
  };

  const updateShippingAddress = async (address: Address) => {
    if (!draft) throw new Error('No draft available');
    await updateDraftMutation.mutateAsync({
      draftId: draft.id,
      data: {
        shipping_first_name: address.first_name,
        shipping_last_name: address.last_name,
        shipping_company: address.company,
        shipping_address_1: address.address_1,
        shipping_address_2: address.address_2,
        shipping_city: address.city,
        shipping_state: address.state,
        shipping_postal_code: address.postal_code,
        shipping_country: address.country,
        shipping_phone: address.phone,
      },
    });
  };

  const finalizeOrder = async () => {
    const result = await finalizeOrderMutation.mutateAsync();
    return result;
  };

  // Auto-create draft on mount if none exists
  useEffect(() => {
    if (!isLoading && !draft) {
      createDraft();
    }
  }, [isLoading, draft]);

  const value = {
    currentStep,
    setCurrentStep,
    draft,
    isLoading,
    createDraft,
    updateBillingAddress,
    updateShippingAddress,
    finalizeOrder,
    isCreatingDraft: createDraftMutation.isPending,
    isUpdatingDraft: updateDraftMutation.isPending,
    isFinalizing: finalizeOrderMutation.isPending,
  };

  return <CheckoutContext.Provider value={value}>{children}</CheckoutContext.Provider>;
}

export function useCheckout() {
  const context = useContext(CheckoutContext);
  if (context === undefined) {
    throw new Error('useCheckout must be used within a CheckoutProvider');
  }
  return context;
}
