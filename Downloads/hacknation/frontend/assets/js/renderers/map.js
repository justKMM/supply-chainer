import { elements } from '../dom.js';
import { state } from '../state.js';

export function renderMap(report) {
  const markers = report.dashboard?.supplier_markers || [];
  const routes = report.dashboard?.supplier_routes || [];

  if (state.mapInstance) { state.mapInstance.remove(); state.mapInstance = null; }

  state.mapInstance = L.map(elements.supplierMap(), {
    zoomControl: true,
    scrollWheelZoom: true,
  }).setView([45.0, 10.5], 6);

  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; CartoDB',
    maxZoom: 18,
  }).addTo(state.mapInstance);

  markers.forEach(m => {
    const markerIcon = L.divIcon({
      className: 'custom-marker',
      html: `<div style="width:14px;height:14px;background:${m.color};border-radius:50%;border:2px solid #fff;box-shadow:0 0 10px ${m.color}"></div>`,
      iconSize: [14, 14],
      iconAnchor: [7, 7],
    });
    L.marker([m.lat, m.lon], { icon: markerIcon })
      .addTo(state.mapInstance)
      .bindPopup(`<b style="color:#333">${m.label}</b><br><span style="color:#666">${m.type}</span>`);
  });

  routes.forEach(r => {
    L.polyline([[r.from.lat, r.from.lon], [r.to.lat, r.to.lon]], {
      color: '#DC143C', weight: 1.5, opacity: 0.5, dashArray: '6,4',
    }).addTo(state.mapInstance);
  });

  setTimeout(() => state.mapInstance.invalidateSize(), 100);
}
