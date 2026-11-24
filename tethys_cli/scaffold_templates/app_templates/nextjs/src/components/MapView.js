'use client';

import 'leaflet/dist/leaflet.css';
import { CircleMarker, MapContainer, Popup, TileLayer } from 'react-leaflet';

// Example points; replace with data from your app's API
const SITES = [
  { name: 'Salt Lake City, UT', position: [40.7608, -111.891] },
  { name: 'Provo, UT', position: [40.2338, -111.6585] },
  { name: 'Logan, UT', position: [41.737, -111.8338] },
];

export default function MapView() {
  return (
    <MapContainer center={[40.8, -111.8]} zoom={8} className="map">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {SITES.map((site) => (
        <CircleMarker key={site.name} center={site.position} radius={9} pathOptions={{ color: '#054b96' }}>
          <Popup>{site.name}</Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
