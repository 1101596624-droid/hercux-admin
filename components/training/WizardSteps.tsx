'use client';

import { Badge } from '@/components/ui';
import { cn } from '@/lib/cn';

interface Step {
  number: number;
  title: string;
  description: string;
}

interface WizardStepsProps {
  steps: Step[];
  currentStep: number;
}

export function WizardSteps({ steps, currentStep }: WizardStepsProps) {
  return (
    <div className="flex items-center justify-between">
      {steps.map((step, index) => (
        <div key={step.number} className="flex items-center flex-1">
          {/* Step Circle */}
          <div className="flex flex-col items-center">
            <div
              className={cn(
                'w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg transition-all',
                currentStep === step.number
                  ? 'bg-primary-600 text-white ring-4 ring-primary-100'
                  : currentStep > step.number
                  ? 'bg-green-600 text-white'
                  : 'bg-dark-200 text-dark-500'
              )}
            >
              {currentStep > step.number ? '✓' : step.number}
            </div>

            <div className="mt-3 text-center">
              <div
                className={cn(
                  'text-sm font-medium',
                  currentStep === step.number
                    ? 'text-primary-600'
                    : currentStep > step.number
                    ? 'text-green-600'
                    : 'text-dark-500'
                )}
              >
                {step.title}
              </div>
              <div className="text-xs text-dark-400 mt-1">
                {step.description}
              </div>
            </div>
          </div>

          {/* Connector Line */}
          {index < steps.length - 1 && (
            <div
              className={cn(
                'flex-1 h-1 mx-4 transition-all',
                currentStep > step.number ? 'bg-green-600' : 'bg-dark-200'
              )}
            />
          )}
        </div>
      ))}
    </div>
  );
}
