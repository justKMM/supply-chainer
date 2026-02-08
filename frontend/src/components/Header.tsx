import React from 'react';
import type { CatalogueProduct } from '../types';

interface HeaderProps {
  onTrigger: () => void;
  isRunning: boolean;
  catalogue: CatalogueProduct[];
  selectedProductId: string;
  onSelectProduct: (productId: string) => void;
  quantity: number;
  onChangeQuantity: (qty: number) => void;
  budgetEur: number;
  onChangeBudget: (budget: number) => void;
  desiredDeliveryDate: string;
  onChangeDesiredDeliveryDate: (date: string) => void;
  catalogueError: string | null;
}

export const Header: React.FC<HeaderProps> = ({
  onTrigger,
  isRunning,
  catalogue,
  selectedProductId,
  onSelectProduct,
  quantity,
  onChangeQuantity,
  budgetEur,
  onChangeBudget,
  desiredDeliveryDate,
  onChangeDesiredDeliveryDate,
  catalogueError,
}) => {
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
          {catalogueError && (
            <p className="mt-1 mb-0 text-[11px] text-orange-400">{catalogueError}</p>
          )}
        </div>
      </div>
      <div className="flex items-center gap-3">
        <div className="hidden md:flex items-center gap-2 text-xs text-text-muted">
          <label className="uppercase tracking-wider">Product</label>
          <select
            className="px-2 py-1 text-xs bg-bg-secondary border border-border rounded"
            value={selectedProductId}
            onChange={(e) => onSelectProduct(e.target.value)}
            disabled={isRunning}
          >
            {catalogue.map((p) => (
              <option key={p.product_id} value={p.product_id}>
                {p.name} (EUR {p.selling_price_eur.toLocaleString()})
              </option>
            ))}
          </select>
        </div>
        <div className="hidden md:flex items-center gap-2 text-xs text-text-muted">
          <label className="uppercase tracking-wider">Qty</label>
          <input
            type="number"
            min={1}
            className="w-16 px-2 py-1 text-xs bg-bg-secondary border border-border rounded"
            value={quantity}
            onChange={(e) => onChangeQuantity(Math.max(1, Number(e.target.value)))}
            disabled={isRunning}
          />
        </div>
        <div className="hidden md:flex items-center gap-2 text-xs text-text-muted">
          <label className="uppercase tracking-wider">Budget</label>
          <input
            type="number"
            min={1}
            className="w-28 px-2 py-1 text-xs bg-bg-secondary border border-border rounded"
            value={budgetEur}
            onChange={(e) => onChangeBudget(Math.max(1, Number(e.target.value)))}
            disabled={isRunning}
          />
        </div>
        <div className="hidden md:flex items-center gap-2 text-xs text-text-muted">
          <label className="uppercase tracking-wider">Delivery</label>
          <input
            type="date"
            className="px-2 py-1 text-xs bg-bg-secondary border border-border rounded"
            value={desiredDeliveryDate}
            onChange={(e) => onChangeDesiredDeliveryDate(e.target.value)}
            disabled={isRunning}
          />
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
      </div>
    </header>
  );
};