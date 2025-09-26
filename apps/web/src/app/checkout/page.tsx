'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useCheckout } from '@/contexts/CheckoutContext';
import { useCart } from '@/contexts/CartContext';
import CheckoutStepper from '@/components/CheckoutStepper';
import AddressForm from '@/components/AddressForm';
import PaymentForm from '@/components/PaymentForm';

export default function CheckoutPage() {
  const router = useRouter();
  const { cart } = useCart();
  const {
    currentStep,
    setCurrentStep,
    draft,
    isLoading,
    updateBillingAddress,
    updateShippingAddress,
    finalizeOrder,
    isUpdatingDraft,
    isFinalizing,
  } = useCheckout();

  const [billingAddress, setBillingAddress] = useState({
    first_name: '',
    last_name: '',
    company: '',
    address_1: '',
    address_2: '',
    city: '',
    state: '',
    postal_code: '',
    country: '',
    phone: '',
  });

  const [shippingAddress, setShippingAddress] = useState({
    first_name: '',
    last_name: '',
    company: '',
    address_1: '',
    address_2: '',
    city: '',
    state: '',
    postal_code: '',
    country: '',
    phone: '',
  });

  const [useSameAddress, setUseSameAddress] = useState(true);
  const [orderId, setOrderId] = useState<number | null>(null);
  const [orderNumber, setOrderNumber] = useState<string>('');

  // Redirect if cart is empty
  useEffect(() => {
    if (cart && cart.items.length === 0) {
      router.push('/cart');
    }
  }, [cart, router]);

  // Load draft data into forms
  useEffect(() => {
    if (draft) {
      setBillingAddress({
        first_name: draft.billing_first_name || '',
        last_name: draft.billing_last_name || '',
        company: draft.billing_company || '',
        address_1: draft.billing_address_1 || '',
        address_2: draft.billing_address_2 || '',
        city: draft.billing_city || '',
        state: draft.billing_state || '',
        postal_code: draft.billing_postal_code || '',
        country: draft.billing_country || '',
        phone: draft.billing_phone || '',
      });

      setShippingAddress({
        first_name: draft.shipping_first_name || '',
        last_name: draft.shipping_last_name || '',
        company: draft.shipping_company || '',
        address_1: draft.shipping_address_1 || '',
        address_2: draft.shipping_address_2 || '',
        city: draft.shipping_city || '',
        state: draft.shipping_state || '',
        postal_code: draft.shipping_postal_code || '',
        country: draft.shipping_country || '',
        phone: draft.shipping_phone || '',
      });
    }
  }, [draft]);

  const steps = [
    {
      id: 1,
      title: 'Billing Address',
      description: 'Enter your billing information',
      completed: currentStep > 1,
    },
    {
      id: 2,
      title: 'Shipping Address',
      description: 'Enter your shipping information',
      completed: currentStep > 2,
    },
    {
      id: 3,
      title: 'Review Order',
      description: 'Review your order details',
      completed: currentStep > 3,
    },
    {
      id: 4,
      title: 'Payment',
      description: 'Complete your payment',
      completed: currentStep > 4,
    },
  ];

  const handleBillingSubmit = async (data: typeof billingAddress) => {
    setBillingAddress(data);
    await updateBillingAddress(data);
    setCurrentStep(2);
  };

  const handleShippingSubmit = async (data: typeof shippingAddress) => {
    setShippingAddress(data);
    await updateShippingAddress(data);
    setCurrentStep(3);
  };

  const handleUseSameAddress = (checked: boolean) => {
    setUseSameAddress(checked);
    if (checked) {
      setShippingAddress(billingAddress);
    }
  };

  const handleFinalizeOrder = async () => {
    try {
      const result = await finalizeOrder();
      setOrderId(result.order_id);
      setOrderNumber(result.order_number);
      setCurrentStep(4); // Move to payment step
    } catch (error) {
      console.error('Failed to finalize order:', error);
      // Handle error (show toast, etc.)
    }
  };

  const handlePaymentSuccess = (orderId: number, orderNumber: string) => {
    router.push(`/orders/${orderId}`);
  };

  const handlePaymentError = (error: string) => {
    console.error('Payment error:', error);
    // Handle error (show toast, etc.)
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!cart || cart.items.length === 0) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Checkout</h1>
          
          <CheckoutStepper
            currentStep={currentStep}
            onStepChange={setCurrentStep}
            steps={steps}
          />

          <div className="bg-white rounded-lg shadow p-6">
            {currentStep === 1 && (
              <AddressForm
                title="Billing Address"
                defaultValues={billingAddress}
                onSubmit={handleBillingSubmit}
                isLoading={isUpdatingDraft}
              />
            )}

            {currentStep === 2 && (
              <div>
                <AddressForm
                  title="Shipping Address"
                  defaultValues={shippingAddress}
                  onSubmit={handleShippingSubmit}
                  onBack={() => setCurrentStep(1)}
                  isLoading={isUpdatingDraft}
                />
                
                <div className="mt-6">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={useSameAddress}
                      onChange={(e) => handleUseSameAddress(e.target.checked)}
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">
                      Use same address for billing and shipping
                    </span>
                  </label>
                </div>
              </div>
            )}

            {currentStep === 3 && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Review Your Order</h2>
                
                {/* Order Summary */}
                <div className="space-y-4 mb-6">
                  <h3 className="text-lg font-medium text-gray-900">Order Items</h3>
                  {cart.items.map((item) => (
                    <div key={item.id} className="flex justify-between items-center py-2 border-b border-gray-200">
                      <div>
                        <p className="font-medium text-gray-900">{item.variant.product.name}</p>
                        <p className="text-sm text-gray-500">{item.variant.name}</p>
                        <p className="text-sm text-gray-500">Qty: {item.quantity}</p>
                      </div>
                      <p className="font-medium text-gray-900">${item.line_total}</p>
                    </div>
                  ))}
                </div>

                {/* Totals */}
                <div className="space-y-2 mb-6">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Subtotal</span>
                    <span className="text-gray-900">${cart.totals.subtotal.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Tax</span>
                    <span className="text-gray-900">${cart.totals.tax_amount.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Shipping</span>
                    <span className="text-gray-900">$10.00</span>
                  </div>
                  <div className="flex justify-between text-lg font-medium border-t border-gray-200 pt-2">
                    <span>Total</span>
                    <span>${(cart.totals.total + 10).toFixed(2)}</span>
                  </div>
                </div>

                {/* Addresses */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Billing Address</h3>
                    <div className="text-sm text-gray-600">
                      <p>{billingAddress.first_name} {billingAddress.last_name}</p>
                      {billingAddress.company && <p>{billingAddress.company}</p>}
                      <p>{billingAddress.address_1}</p>
                      {billingAddress.address_2 && <p>{billingAddress.address_2}</p>}
                      <p>{billingAddress.city}, {billingAddress.state} {billingAddress.postal_code}</p>
                      <p>{billingAddress.country}</p>
                      {billingAddress.phone && <p>{billingAddress.phone}</p>}
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Shipping Address</h3>
                    <div className="text-sm text-gray-600">
                      <p>{shippingAddress.first_name} {shippingAddress.last_name}</p>
                      {shippingAddress.company && <p>{shippingAddress.company}</p>}
                      <p>{shippingAddress.address_1}</p>
                      {shippingAddress.address_2 && <p>{shippingAddress.address_2}</p>}
                      <p>{shippingAddress.city}, {shippingAddress.state} {shippingAddress.postal_code}</p>
                      <p>{shippingAddress.country}</p>
                      {shippingAddress.phone && <p>{shippingAddress.phone}</p>}
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex justify-between pt-6">
                  <button
                    onClick={() => setCurrentStep(2)}
                    className="px-6 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    Back to Shipping
                  </button>
                  
                  <button
                    onClick={handleFinalizeOrder}
                    disabled={isFinalizing}
                    className="px-6 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isFinalizing ? 'Processing...' : 'Place Order'}
                  </button>
                </div>
              </div>
            )}

            {currentStep === 4 && orderId && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Complete Payment</h2>
                <PaymentForm
                  orderId={orderId}
                  orderNumber={orderNumber}
                  total={cart.totals.total + 10} // Include shipping
                  onSuccess={handlePaymentSuccess}
                  onError={handlePaymentError}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
