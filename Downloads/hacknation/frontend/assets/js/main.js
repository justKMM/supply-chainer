import { elements } from './dom.js';
import { state } from './state.js';
import { startSSE } from './sse.js';
import { triggerCascadeRequest, fetchProgress, fetchReport } from './api.js';
import { renderMetrics } from './renderers/metrics.js';
import { renderNetworkGraph } from './renderers/network.js';
import { renderMap } from './renderers/map.js';
import { renderCostChart } from './renderers/costChart.js';
import { renderTimeline } from './renderers/timeline.js';
import { renderNegotiations } from './renderers/negotiations.js';
import { renderRisks } from './renderers/risks.js';
import { renderCompliance } from './renderers/compliance.js';
import { renderDiscovery } from './renderers/discovery.js';
import { renderIntelligence } from './renderers/intelligence.js';
import { renderPubSub } from './renderers/pubsub.js';
import { renderReputation } from './renderers/reputation.js';
import { renderReasoning } from './renderers/reasoning.js';

function setRunningState(isRunning) {
  const btn = elements.triggerBtn();
  if (isRunning) {
    btn.disabled = true;
    btn.textContent = 'Cascade Running...';
    btn.classList.add('running');
    elements.emptyState().style.display = 'none';
    elements.dashboard().style.display = 'block';
    elements.progressContainer().classList.add('active');
    elements.feedContainer().innerHTML = '';
    state.messageCount = 0;
  } else {
    elements.progressContainer().classList.remove('active');
    btn.disabled = false;
    btn.textContent = 'Buy Ferrari in One Click';
    btn.classList.remove('running');
  }
}

async function triggerCascade() {
  setRunningState(true);
  startSSE();

  try {
    await triggerCascadeRequest();
  } catch (e) {
    console.error('Trigger failed:', e);
  }

  pollProgress();
}

async function pollProgress() {
  const interval = setInterval(async () => {
    try {
      const data = await fetchProgress();
      elements.progressBar().style.width = `${data.progress}%`;

      const stages = [
        [0, 'Initializing agent network & event subscriptions...'],
        [10, 'Decomposing intent into Bill of Materials...'],
        [20, 'Discovering suppliers across registry...'],
        [40, 'Requesting quotes from qualified suppliers...'],
        [55, 'Negotiating prices with suppliers...'],
        [70, 'Running compliance checks...'],
        [80, 'Issuing purchase orders...'],
        [88, 'Planning logistics routes...'],
        [91, 'Simulating disruption & recovery...'],
        [93, 'Recording transaction attestations...'],
        [95, 'Scanning intelligence feeds (weather, regulatory, commodity)...'],
        [97, 'Generating final report...'],
      ];
      let stageText = 'Processing...';
      for (const [thresh, text] of stages) {
        if (data.progress >= thresh) stageText = text;
      }
      elements.progressLabel().textContent = `${data.progress}% — ${stageText}`;

      if (!data.running && data.progress >= 100) {
        clearInterval(interval);
        setRunningState(false);
        loadReport();
      }
    } catch (e) {}
  }, 500);
}

async function loadReport() {
  try {
    state.reportData = await fetchReport();
    renderDashboard(state.reportData);
  } catch (e) {
    console.error('Failed to load report:', e);
    setTimeout(loadReport, 2000);
  }
}

function renderDashboard(report) {
  renderMetrics(report);
  renderNetworkGraph(report);
  renderMap(report);
  renderCostChart(report);
  renderTimeline(report);
  renderNegotiations(report);
  renderRisks(report);
  renderCompliance(report);
  renderDiscovery(report);
  renderIntelligence(report);
  renderPubSub(report);
  renderReputation(report);
  renderReasoning(report);
}

window.triggerCascade = triggerCascade;
