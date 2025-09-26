'use client';

import { useAuth } from '@/contexts/AuthContext';

export default function RoleBadge() {
  const { user, isAdmin } = useAuth();

  if (!user) return null;

  return (
    <div className="flex items-center space-x-2">
      <span className="text-sm text-gray-600">
        {user.first_name} {user.last_name}
      </span>
      <span
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          isAdmin
            ? 'bg-red-100 text-red-800'
            : 'bg-green-100 text-green-800'
        }`}
      >
        {isAdmin ? 'Admin' : 'Customer'}
      </span>
    </div>
  );
}
