'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface CheckoutStepperProps {
  currentStep: number;
  onStepChange: (step: number) => void;
  steps: Array<{
    id: number;
    title: string;
    description: string;
    completed: boolean;
  }>;
}

export default function CheckoutStepper({ currentStep, onStepChange, steps }: CheckoutStepperProps) {
  return (
    <nav aria-label="Progress" className="mb-8">
      <ol className="flex items-center justify-center space-x-8">
        {steps.map((step, stepIdx) => (
          <li key={step.id} className="relative">
            {stepIdx !== steps.length - 1 ? (
              <div className="absolute top-4 left-4 -ml-px mt-0.5 h-full w-0.5 bg-gray-300" />
            ) : null}
            <div className="group relative flex items-start">
              <span className="flex h-9 items-center">
                <span
                  className={`relative z-10 flex h-8 w-8 items-center justify-center rounded-full border-2 ${
                    step.completed
                      ? 'border-indigo-600 bg-indigo-600'
                      : currentStep === step.id
                      ? 'border-indigo-600 bg-white'
                      : 'border-gray-300 bg-white'
                  }`}
                >
                  {step.completed ? (
                    <svg
                      className="h-5 w-5 text-white"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  ) : (
                    <span
                      className={`text-sm font-medium ${
                        currentStep === step.id ? 'text-indigo-600' : 'text-gray-500'
                      }`}
                    >
                      {step.id}
                    </span>
                  )}
                </span>
              </span>
              <span className="ml-4 min-w-0 flex flex-col">
                <span
                  className={`text-sm font-medium ${
                    currentStep === step.id ? 'text-indigo-600' : 'text-gray-500'
                  }`}
                >
                  {step.title}
                </span>
                <span className="text-sm text-gray-500">{step.description}</span>
              </span>
            </div>
          </li>
        ))}
      </ol>
    </nav>
  );
}
