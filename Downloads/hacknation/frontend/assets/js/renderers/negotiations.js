import { elements } from '../dom.js';

export function renderNegotiations(report) {
  const negotiations = report.negotiations || [];
  const container = elements.negotiationContainer();

  container.innerHTML = negotiations.map(n => `
    <div class="negotiation-item">
      <div class="negotiation-header">
        <div>
          <div class="negotiation-product">${n.product}</div>
          <div class="negotiation-supplier">${n.with_name || n.with_agent}</div>
        </div>
        <span class="risk-badge low">${n.rounds} rounds</span>
      </div>
      <div class="negotiation-rounds">
        <div class="negotiation-round">
          <span class="label">Ask</span>
          <span class="price" style="color:#F44336">EUR ${n.initial_ask_eur?.toLocaleString()}</span>
        </div>
        <span class="negotiation-arrow">\u2192</span>
        <div class="negotiation-round">
          <span class="label">Offer</span>
          <span class="price" style="color:#FF9800">EUR ${n.initial_offer_eur?.toLocaleString()}</span>
        </div>
        <span class="negotiation-arrow">\u2192</span>
        <div class="negotiation-round">
          <span class="label">Agreed</span>
          <span class="price" style="color:#4CAF50">EUR ${n.final_agreed_eur?.toLocaleString()}</span>
        </div>
      </div>
      <div class="negotiation-savings">Discount: ${n.discount_pct?.toFixed(1)}%</div>
    </div>
  `).join('') || '<div class="empty-state"><p>No negotiations yet</p></div>';
}
