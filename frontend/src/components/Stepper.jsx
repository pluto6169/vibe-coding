import React from 'react';

export default function Stepper({ currentStep, completedSteps = [] }) {
  const steps = [
    { label: 'Upload Files', icon: '📤' },
    { label: 'Review Extracted Text', icon: '📝' },
    { label: 'Results & Export', icon: '📊' }
  ];

  return (
    <div className="stepper">
      {steps.map((step, index) => {
        let className = 'stepper-step';
        if (index === currentStep) className += ' active';
        if (completedSteps.includes(index)) className += ' completed';

        return (
          <div key={index} className={className}>
            <div className="step-icon">
              {completedSteps.includes(index) && index !== currentStep ? '✓' : step.icon}
            </div>
            <span>{step.label}</span>
          </div>
        );
      })}
    </div>
  );
}
