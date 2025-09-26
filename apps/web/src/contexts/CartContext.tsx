'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api';

interface CartItem {
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

interface Cart {
  id: number;
  items: CartItem[];
  totals: {
    subtotal: number;
    tax_amount: number;
    total: number;
    item_count: number;
  };
}

interface CartContextType {
  cart: Cart | null;
  isLoading: boolean;
  addToCart: (variantId: number, quantity?: number) => Promise<void>;
  updateCartItem: (itemId: number, quantity: number) => Promise<void>;
  removeFromCart: (itemId: number) => Promise<void>;
  clearCart: () => Promise<void>;
  isAddingToCart: boolean;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: React.ReactNode }) {
  const [isAddingToCart, setIsAddingToCart] = useState(false);
  const queryClient = useQueryClient();

  // Fetch cart
  const { data: cart, isLoading } = useQuery<Cart>({
    queryKey: ['cart'],
    queryFn: async () => {
      const response = await apiClient.get('/cart/');
      return response.data;
    },
    retry: false,
  });

  // Add to cart mutation
  const addToCartMutation = useMutation({
    mutationFn: async ({ variantId, quantity = 1 }: { variantId: number; quantity: number }) => {
      const response = await apiClient.post('/cart/items/', {
        variant_id: variantId,
        quantity,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });

  // Update cart item mutation
  const updateCartItemMutation = useMutation({
    mutationFn: async ({ itemId, quantity }: { itemId: number; quantity: number }) => {
      const response = await apiClient.patch(`/cart/items/${itemId}/`, {
        quantity,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });

  // Remove from cart mutation
  const removeFromCartMutation = useMutation({
    mutationFn: async (itemId: number) => {
      await apiClient.delete(`/cart/items/${itemId}/delete/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });

  // Clear cart mutation
  const clearCartMutation = useMutation({
    mutationFn: async () => {
      await apiClient.post('/cart/clear/');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });

  const addToCart = async (variantId: number, quantity: number = 1) => {
    try {
      setIsAddingToCart(true);
      await addToCartMutation.mutateAsync({ variantId, quantity });
    } finally {
      setIsAddingToCart(false);
    }
  };

  const updateCartItem = async (itemId: number, quantity: number) => {
    await updateCartItemMutation.mutateAsync({ itemId, quantity });
  };

  const removeFromCart = async (itemId: number) => {
    await removeFromCartMutation.mutateAsync(itemId);
  };

  const clearCart = async () => {
    await clearCartMutation.mutateAsync();
  };

  const value = {
    cart,
    isLoading,
    addToCart,
    updateCartItem,
    removeFromCart,
    clearCart,
    isAddingToCart,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}
