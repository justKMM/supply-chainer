import { elements } from '../dom.js';
import { state } from '../state.js';

export function renderCostChart(report) {
  const items = report.dashboard?.cost_breakdown || [];
  if (state.costChartInstance) state.costChartInstance.destroy();

  const ctx = elements.costChart().getContext('2d');
  state.costChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: items.map(i => i.label),
      datasets: [{
        data: items.map(i => i.value),
        backgroundColor: items.map(i => i.color),
        borderWidth: 0,
        hoverOffset: 8,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '65%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: '#888', font: { size: 11, family: 'Inter' }, padding: 12 }
        },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.label}: EUR ${ctx.parsed.toLocaleString()}`
          }
        }
      }
    }
  });
}
