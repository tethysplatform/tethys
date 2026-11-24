const PORTAL_HOST = process.env.NEXT_PUBLIC_TETHYS_PORTAL_HOST || '';
const PREFIX = (process.env.NEXT_PUBLIC_TETHYS_PREFIX_URL ?? '').replace(/^\/|\/$/g, '');
const PORTAL_BASE = PREFIX ? `${PORTAL_HOST}/${PREFIX}` : PORTAL_HOST;
const APP_ROOT_URL = process.env.NEXT_PUBLIC_TETHYS_APP_ROOT_URL || '/';

// Same address as TETHYS_DEV_SERVER in next.config.mjs
const TETHYS_DEV_SERVER = 'http://localhost:8000';

const ACCESS_TOKEN_KEY = 'jwt_access';
const REFRESH_TOKEN_KEY = 'jwt_refresh';

export class NotLoggedInError extends Error {
  constructor() {
    super('Not logged in to Tethys');
    this.name = 'NotLoggedInError';
  }
}

export function loginUrl() {
  // Django rejects logins sent through the Next.js dev server (CSRF origin check),
  // so in development log in on the Tethys server itself
  if (process.env.NODE_ENV === 'development') {
    return `${TETHYS_DEV_SERVER}/accounts/login/`;
  }
  return `${PORTAL_BASE}/accounts/login/?next=${encodeURIComponent(window.location.pathname)}`;
}

function getCookie(name) {
  return document.cookie
    .split('; ')
    .find((row) => row.startsWith(`${name}=`))
    ?.split('=')[1];
}

function isLoginPage(response) {
  return response.redirected && new URL(response.url).pathname.endsWith('/accounts/login/');
}

async function request(path, options = {}) {
  const response = await fetch(`${PORTAL_BASE}${path}`, {
    credentials: 'include',
    ...options,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken') ?? '',
      ...options.headers,
    },
  });

  // Tethys answers a logged-out request by redirecting to its login page
  if (response.status === 401 || isLoginPage(response)) {
    throw new NotLoggedInError();
  }
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json();
}

export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

async function getJWTToken() {
  const { access, refresh } = await request('/api/token/');
  localStorage.setItem(ACCESS_TOKEN_KEY, access);
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
  return { access, refresh };
}

async function refreshJWTToken() {
  const { access } = await request('/api/token/refresh/', {
    method: 'POST',
    body: JSON.stringify({ refresh: getRefreshToken() }),
  });
  localStorage.setItem(ACCESS_TOKEN_KEY, access);
  return access;
}

export const tethysAPI = {
  getJWTToken,
  refreshJWTToken,
  getUserData: () => request('/api/whoami/'),
  getAppData: () => request(`/api/apps/${process.env.NEXT_PUBLIC_TETHYS_APP_ID}/`),
};

export const appAPI = {
  getData: () => request(`${APP_ROOT_URL}data/`),
};