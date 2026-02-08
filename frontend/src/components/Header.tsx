import React from 'react';

interface HeaderProps {
  onTrigger: () => void;
  isRunning: boolean;
}

export const Header: React.FC<HeaderProps> = ({ onTrigger, isRunning }) => {
  return (
    <header className="sticky top-0 z-50 flex items-center justify-between px-10 py-5 border-b border-border bg-gradient-to-br from-bg-secondary to-[#0d0d18]">
      <div className="flex items-center gap-4">
        <div className="flex items-center justify-center w-12 h-12 text-2xl font-black text-white rounded-xl bg-ferrari-red shadow-[0_0_20px_theme('colors.glow-red')]">
          F
        </div>
        <div>
          <h1 className="m-0 text-xl font-bold text-transparent bg-gradient-to-r from-ferrari-red to-[#ff6b6b] bg-clip-text">
            Ferrari Supply Chain Agents
          </h1>
          <p className="mt-0.5 mb-0 text-xs text-text-secondary">
            NANDA-Native Internet of Agents &mdash; One Click Procurement
          </p>
        </div>
      </div>
      <button 
        className={`px-8 py-3.5 text-[15px] font-bold text-white uppercase tracking-widest rounded-xl transition-all duration-300 font-sans ${
          isRunning 
            ? 'bg-gradient-to-br from-[#333] to-[#222] cursor-not-allowed shadow-[0_4px_20px_rgba(0,0,0,0.4)]' 
            : 'bg-gradient-to-br from-ferrari-red to-ferrari-dark cursor-pointer shadow-[0_4px_20px_rgba(220,20,60,0.4)] hover:shadow-[0_4px_25px_rgba(220,20,60,0.6)]'
        }`}
        onClick={onTrigger}
        disabled={isRunning}
      >
        {isRunning ? 'Cascade Running...' : 'Buy Ferrari in One Click'}
      </button>
    </header>
  );
};