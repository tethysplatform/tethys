'use client';

import dynamic from 'next/dynamic';

// Leaflet needs the browser's window object, so load it only on the client
const MapView = dynamic(() => import('@/components/MapView'), {
  ssr: false,
  loading: () => <p>Loading map…</p>,
});

export default function MapPage() {
  return (
    <main className="map-page">
      <MapView />
    </main>
  );
}
