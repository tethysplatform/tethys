'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import { tethysAPI } from '@/services/api';
// Imported (not in public/) so it is served from the app's static folder
import logo from '@/assets/logo.png';

const NAV_LINKS = [
  { href: '/', label: 'Home', icon: '🏠' },
  { href: '/map/', label: 'Map', icon: '🗺️' },
];

// Tethys portal pages live outside the app's basePath, so use plain links for them
const PORTAL_PREFIX = (process.env.NEXT_PUBLIC_TETHYS_PREFIX_URL ?? '').replace(/^\/|\/$/g, '');
const PORTAL_ROOT = PORTAL_PREFIX ? `/${PORTAL_PREFIX}` : '';

const trim = (path) => path.replace(/\/$/, '');

export default function AppShell({ children }) {
  const pathname = trim(usePathname() ?? '');
  const [navOpen, setNavOpen] = useState(true);
  const [user, setUser] = useState(null);

  useEffect(() => {
    tethysAPI.getUserData().then(setUser).catch(() => setUser(null));
  }, []);

  return (
    <div className={`app ${navOpen ? 'show-nav' : 'hide-nav'}`}>
      <header className="app-header">
        <button className="toggle-nav" onClick={() => setNavOpen((open) => !open)} aria-label="Toggle navigation">
          <span />
          <span />
          <span />
        </button>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={logo.src} alt="" className="app-logo" />
        <span className="app-title">{process.env.NEXT_PUBLIC_TETHYS_APP_NAME}</span>
        <div className="header-right">
          {user?.isAuthenticated && <span className="header-username">{user.username}</span>}
          <a href={`${PORTAL_ROOT}/apps/`} className="header-exit">
            Exit
          </a>
        </div>
      </header>

      <div className="app-body">
        <nav className="app-sidebar">
          <p className="nav-heading">App Navigation</p>
          <ul>
            {NAV_LINKS.map(({ href, label, icon }) => (
              <li key={href}>
                <Link href={href} className={pathname === trim(href) ? 'active' : undefined}>
                  <span className="nav-icon">{icon}</span>
                  {label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
        <div className="app-content">{children}</div>
      </div>
    </div>
  );
}
