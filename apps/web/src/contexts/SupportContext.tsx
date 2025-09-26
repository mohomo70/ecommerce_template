'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

interface SupportTicket {
  id: number;
  ticket_number: string;
  subject: string;
  description: string;
  category: string;
  priority: string;
  status: string;
  assigned_to: number | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
  messages: TicketMessage[];
}

interface TicketMessage {
  id: number;
  ticket: number;
  sender: number;
  message: string;
  is_internal: boolean;
  created_at: string;
}

interface FAQ {
  id: number;
  question: string;
  answer: string;
  category: string;
  is_published: boolean;
  order: number;
  created_at: string;
  updated_at: string;
}

interface ProductReview {
  id: number;
  product: number;
  customer: number;
  rating: number;
  title: string;
  review: string;
  is_verified_purchase: boolean;
  is_approved: boolean;
  helpful_votes: number;
  created_at: string;
  updated_at: string;
}

interface SupportContextType {
  tickets: SupportTicket[];
  faqs: FAQ[];
  reviews: ProductReview[];
  loading: boolean;
  error: string | null;
  createTicket: (ticketData: Partial<SupportTicket>) => Promise<void>;
  updateTicket: (ticketId: number, updates: Partial<SupportTicket>) => Promise<void>;
  addMessage: (ticketId: number, message: string) => Promise<void>;
  fetchTickets: () => Promise<void>;
  fetchFAQs: () => Promise<void>;
  fetchReviews: (productId?: number) => Promise<void>;
  createReview: (reviewData: Partial<ProductReview>) => Promise<void>;
  voteReview: (reviewId: number, isHelpful: boolean) => Promise<void>;
}

const SupportContext = createContext<SupportContextType | undefined>(undefined);

export const useSupport = () => {
  const context = useContext(SupportContext);
  if (!context) {
    throw new Error('useSupport must be used within a SupportProvider');
  }
  return context;
};

export const SupportProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuth();
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [faqs, setFaqs] = useState<FAQ[]>([]);
  const [reviews, setReviews] = useState<ProductReview[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiCall = async (endpoint: string, options: RequestInit = {}) => {
    const response = await fetch(`/api/support${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API call failed: ${response.statusText}`);
    }

    return response.json();
  };

  const createTicket = async (ticketData: Partial<SupportTicket>) => {
    try {
      setLoading(true);
      const newTicket = await apiCall('/tickets/', {
        method: 'POST',
        body: JSON.stringify(ticketData),
      });
      setTickets(prev => [newTicket, ...prev]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create ticket');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateTicket = async (ticketId: number, updates: Partial<SupportTicket>) => {
    try {
      setLoading(true);
      const updatedTicket = await apiCall(`/tickets/${ticketId}/`, {
        method: 'PATCH',
        body: JSON.stringify(updates),
      });
      setTickets(prev => prev.map(ticket => 
        ticket.id === ticketId ? updatedTicket : ticket
      ));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update ticket');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const addMessage = async (ticketId: number, message: string) => {
    try {
      setLoading(true);
      const newMessage = await apiCall(`/tickets/${ticketId}/messages/`, {
        method: 'POST',
        body: JSON.stringify({ message }),
      });
      setTickets(prev => prev.map(ticket => 
        ticket.id === ticketId 
          ? { ...ticket, messages: [...ticket.messages, newMessage] }
          : ticket
      ));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add message');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const fetchTickets = async () => {
    try {
      setLoading(true);
      const ticketsData = await apiCall('/tickets/');
      setTickets(ticketsData.results || ticketsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tickets');
    } finally {
      setLoading(false);
    }
  };

  const fetchFAQs = async () => {
    try {
      setLoading(true);
      const faqsData = await apiCall('/faq/');
      setFaqs(faqsData.results || faqsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch FAQs');
    } finally {
      setLoading(false);
    }
  };

  const fetchReviews = async (productId?: number) => {
    try {
      setLoading(true);
      const endpoint = productId ? `/reviews/product/${productId}/` : '/reviews/';
      const reviewsData = await apiCall(endpoint);
      setReviews(reviewsData.results || reviewsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch reviews');
    } finally {
      setLoading(false);
    }
  };

  const createReview = async (reviewData: Partial<ProductReview>) => {
    try {
      setLoading(true);
      const newReview = await apiCall('/reviews/', {
        method: 'POST',
        body: JSON.stringify(reviewData),
      });
      setReviews(prev => [newReview, ...prev]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create review');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const voteReview = async (reviewId: number, isHelpful: boolean) => {
    try {
      setLoading(true);
      await apiCall(`/reviews/${reviewId}/vote/`, {
        method: 'POST',
        body: JSON.stringify({ is_helpful: isHelpful }),
      });
      // Update the review's helpful votes count
      setReviews(prev => prev.map(review => 
        review.id === reviewId 
          ? { ...review, helpful_votes: review.helpful_votes + (isHelpful ? 1 : -1) }
          : review
      ));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to vote on review');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchTickets();
      fetchFAQs();
    }
  }, [user]);

  const value: SupportContextType = {
    tickets,
    faqs,
    reviews,
    loading,
    error,
    createTicket,
    updateTicket,
    addMessage,
    fetchTickets,
    fetchFAQs,
    fetchReviews,
    createReview,
    voteReview,
  };

  return (
    <SupportContext.Provider value={value}>
      {children}
    </SupportContext.Provider>
  );
};
