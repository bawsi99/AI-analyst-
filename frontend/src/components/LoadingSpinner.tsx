import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  className?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  text, 
  className = '' 
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8'
  };

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <div className="text-center">
        <div className={`loading-spinner mx-auto ${sizeClasses[size]}`}></div>
        {text && (
          <p className="text-gray-600 mt-2 text-sm">{text}</p>
        )}
      </div>
    </div>
  );
};

export default LoadingSpinner; 