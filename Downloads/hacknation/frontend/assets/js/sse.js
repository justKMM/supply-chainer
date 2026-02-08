import { elements } from './dom.js';
import { state } from './state.js';
import { TYPE_COLORS, TYPE_ICONS } from './constants.js';

export function startSSE() {
  if (state.eventSource) {
    state.eventSource.close();
  }
  state.eventSource = new EventSource('/api/stream');
  state.eventSource.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.type === 'heartbeat') return;
    addMessageToFeed(msg);
  };
}

function addMessageToFeed(msg) {
  state.messageCount += 1;
  elements.msgCount().textContent = `${state.messageCount} messages`;
  const container = elements.feedContainer();
  const color = TYPE_COLORS[msg.type] || '#666';
  const icon = TYPE_ICONS[msg.type] || '\u2139\uFE0F';
  const time = msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : '';

  const div = document.createElement('div');
  div.className = 'feed-msg';
  div.innerHTML = `
    <div class="feed-msg-header">
      <span>${icon}</span>
      <span class="feed-badge" style="background:${color}22;color:${color}">${msg.type.replace(/_/g,' ')}</span>
      <span class="feed-from">${msg.from_label||msg.from_id||''}</span>
      <span class="feed-arrow">\u2192</span>
      <span class="feed-to">${msg.to_label||msg.to_id||''}</span>
      <span class="feed-time">${time}</span>
    </div>
    <div class="feed-summary">${msg.summary||''}</div>
    ${msg.detail ? `<div class="feed-detail">${msg.detail}</div>` : ''}
  `;
  container.insertBefore(div, container.firstChild);

  while (container.children.length > 100) {
    container.removeChild(container.lastChild);
  }
}
