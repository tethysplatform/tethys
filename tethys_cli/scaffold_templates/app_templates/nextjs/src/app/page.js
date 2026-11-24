'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { appAPI, loginUrl, NotLoggedInError } from '@/services/api';

export default function Home() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    appAPI.getData().then(setData).catch(setError);
  }, []);

  return (
    <main className="page">
      <section className="hero">
        <h1>{process.env.NEXT_PUBLIC_TETHYS_APP_NAME}</h1>
        <p>A Tethys app with a Next.js frontend. Edit <code>src/app/page.js</code> to change this page.</p>
        <Link href="/map/" className="button">
          Open the map
        </Link>
      </section>

      <section className="cards">
        <div className="card">
          <h2>Map</h2>
          <p>An interactive Leaflet map with example sites. See <code>src/components/MapView.js</code>.</p>
        </div>
        <div className="card">
          <h2>Data from Tethys</h2>
          <DataPreview data={data} error={error} />
        </div>
      </section>
    </main>
  );
}

function DataPreview({ data, error }) {
  if (error instanceof NotLoggedInError) {
    return (
      <p>
        You&apos;re not logged in. <a href={loginUrl()}>Log in to Tethys</a>, then reload this page.
      </p>
    );
  }
  if (error) return <p className="error">Could not reach Tethys: {error.message}</p>;
  if (!data) return <p>Loading…</p>;
  return (
    <>
      <p>
        Returned by the <code>data</code> controller in <code>controllers.py</code>:
      </p>
      <pre>{JSON.stringify(data.series, null, 2)}</pre>
    </>
  );
}
