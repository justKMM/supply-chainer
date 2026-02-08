import React from 'react';

interface ProgressBarProps {
  progress: number;
  label?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ progress, label }) => {
  return (
    <div className="px-10 mb-5">
      <div className="h-1 overflow-hidden rounded-sm bg-bg-card">
        <div 
          className="h-full rounded-sm bg-gradient-to-r from-ferrari-red via-[#ff6b6b] to-accent-orange transition-[width] duration-500 ease-linear"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      <div className="mt-1 text-[11px] text-center text-text-secondary">
        {progress}% — {label || 'Processing...'}
      </div>
    </div>
  );
};