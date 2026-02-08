import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import type { MapMarker, MapRoute } from '../types';

interface MapProps {
  markers: MapMarker[];
  routes: MapRoute[];
}

// Fix for default Leaflet markers in React
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
});

const createCustomIcon = (color: string) => L.divIcon({
  className: 'custom-marker',
  html: `<div style="width:14px;height:14px;background:${color};border-radius:50%;border:2px solid #fff;box-shadow:0 0 10px ${color}"></div>`,
  iconSize: [14, 14],
  iconAnchor: [7, 7],
});

export const SupplierMap: React.FC<MapProps> = ({ markers, routes }) => {
  return (
    <MapContainer 
      center={[45.0, 10.5]} 
      zoom={6} 
      scrollWheelZoom={true} 
      className="w-full h-[350px] rounded-b-[14px]"
    >
      <TileLayer
        attribution='&copy; CartoDB'
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
      />
      {markers.map((m, idx) => (
        <Marker key={idx} position={[m.lat, m.lon]} icon={createCustomIcon(m.color)}>
          <Popup>
            <b className="text-[#333]">{m.label}</b><br />
            <span className="text-[#666]">{m.type}</span>
          </Popup>
        </Marker>
      ))}
      {routes.map((r, idx) => (
        <Polyline 
          key={idx}
          positions={[[r.from.lat, r.from.lon], [r.to.lat, r.to.lon]]}
          pathOptions={{ color: '#DC143C', weight: 1.5, opacity: 0.5, dashArray: '6,4' }} 
        />
      ))}
    </MapContainer>
  );
};