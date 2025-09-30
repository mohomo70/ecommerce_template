"use client";

import { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "@/contexts/AuthContext";
import { CartProvider } from "@/contexts/CartContext";
import { CheckoutProvider } from "@/contexts/CheckoutContext";
import { PaymentProvider } from "@/contexts/PaymentContext";
import { SupportProvider } from "@/contexts/SupportContext";
import { AnalyticsProvider } from "@/contexts/AnalyticsContext";
import ErrorBoundary from "@/components/ErrorBoundary";

export default function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <CartProvider>
          <CheckoutProvider>
            <PaymentProvider>
              <SupportProvider>
                <AnalyticsProvider>
                  <ErrorBoundary>
                    {children}
                  </ErrorBoundary>
                </AnalyticsProvider>
              </SupportProvider>
            </PaymentProvider>
          </CheckoutProvider>
        </CartProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}
