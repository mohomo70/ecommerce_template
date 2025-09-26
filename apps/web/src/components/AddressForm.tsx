'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const addressSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  company: z.string().optional(),
  address_1: z.string().min(1, 'Address is required'),
  address_2: z.string().optional(),
  city: z.string().min(1, 'City is required'),
  state: z.string().min(1, 'State is required'),
  postal_code: z.string().min(3, 'Postal code is required'),
  country: z.string().min(1, 'Country is required'),
  phone: z.string().optional(),
});

type AddressFormData = z.infer<typeof addressSchema>;

interface AddressFormProps {
  title: string;
  defaultValues?: Partial<AddressFormData>;
  onSubmit: (data: AddressFormData) => void;
  onBack?: () => void;
  onNext?: () => void;
  isLoading?: boolean;
}

export default function AddressForm({
  title,
  defaultValues,
  onSubmit,
  onBack,
  onNext,
  isLoading = false,
}: AddressFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
  } = useForm<AddressFormData>({
    resolver: zodResolver(addressSchema),
    defaultValues,
    mode: 'onChange',
  });

  const handleFormSubmit = (data: AddressFormData) => {
    onSubmit(data);
    if (onNext && isValid) {
      onNext();
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">{title}</h2>
      
      <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div>
            <label htmlFor="first_name" className="block text-sm font-medium text-gray-700">
              First Name *
            </label>
            <input
              {...register('first_name')}
              type="text"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              placeholder="Enter your first name"
            />
            {errors.first_name && (
              <p className="mt-1 text-sm text-red-600">{errors.first_name.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="last_name" className="block text-sm font-medium text-gray-700">
              Last Name *
            </label>
            <input
              {...register('last_name')}
              type="text"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              placeholder="Enter your last name"
            />
            {errors.last_name && (
              <p className="mt-1 text-sm text-red-600">{errors.last_name.message}</p>
            )}
          </div>
        </div>

        <div>
          <label htmlFor="company" className="block text-sm font-medium text-gray-700">
            Company
          </label>
          <input
            {...register('company')}
            type="text"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            placeholder="Enter your company name (optional)"
          />
        </div>

        <div>
          <label htmlFor="address_1" className="block text-sm font-medium text-gray-700">
            Address Line 1 *
          </label>
          <input
            {...register('address_1')}
            type="text"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            placeholder="Enter your street address"
          />
          {errors.address_1 && (
            <p className="mt-1 text-sm text-red-600">{errors.address_1.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="address_2" className="block text-sm font-medium text-gray-700">
            Address Line 2
          </label>
          <input
            {...register('address_2')}
            type="text"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            placeholder="Apartment, suite, etc. (optional)"
          />
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
          <div>
            <label htmlFor="city" className="block text-sm font-medium text-gray-700">
              City *
            </label>
            <input
              {...register('city')}
              type="text"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              placeholder="Enter your city"
            />
            {errors.city && (
              <p className="mt-1 text-sm text-red-600">{errors.city.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="state" className="block text-sm font-medium text-gray-700">
              State *
            </label>
            <input
              {...register('state')}
              type="text"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              placeholder="Enter your state"
            />
            {errors.state && (
              <p className="mt-1 text-sm text-red-600">{errors.state.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="postal_code" className="block text-sm font-medium text-gray-700">
              Postal Code *
            </label>
            <input
              {...register('postal_code')}
              type="text"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              placeholder="Enter your postal code"
            />
            {errors.postal_code && (
              <p className="mt-1 text-sm text-red-600">{errors.postal_code.message}</p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div>
            <label htmlFor="country" className="block text-sm font-medium text-gray-700">
              Country *
            </label>
            <select
              {...register('country')}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            >
              <option value="">Select your country</option>
              <option value="US">United States</option>
              <option value="CA">Canada</option>
              <option value="GB">United Kingdom</option>
              <option value="DE">Germany</option>
              <option value="FR">France</option>
              <option value="ES">Spain</option>
              <option value="IT">Italy</option>
              <option value="AU">Australia</option>
            </select>
            {errors.country && (
              <p className="mt-1 text-sm text-red-600">{errors.country.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
              Phone Number
            </label>
            <input
              {...register('phone')}
              type="tel"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              placeholder="Enter your phone number (optional)"
            />
          </div>
        </div>

        <div className="flex justify-between pt-6">
          {onBack && (
            <button
              type="button"
              onClick={onBack}
              className="px-6 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Back
            </button>
          )}
          
          <button
            type="submit"
            disabled={!isValid || isLoading}
            className="px-6 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Saving...' : onNext ? 'Continue' : 'Save'}
          </button>
        </div>
      </form>
    </div>
  );
}
