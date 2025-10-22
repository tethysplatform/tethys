export function getTethysPortalHost() {
  let tethys_portal_host = process.env.TETHYS_PORTAL_HOST;

  // If the .env property is not set, derive from current location
  if (!tethys_portal_host || !tethys_portal_host.length) {
    let currLocation = window.location.href;
    let url = new URL(currLocation);
    tethys_portal_host = url.origin;
  }

  return tethys_portal_host;
}

export function getTethysPortalBase() {
  let tethys_portal_host = getTethysPortalHost();
  let tethys_prefix_url = process.env.TETHYS_PREFIX_URL.replace(/^\/|\/$/g, "");
  tethys_prefix_url = `/${tethys_prefix_url}`;
  return tethys_portal_host + tethys_prefix_url.replace(/\/{2,}/g, "/");
}

export function getTethysAppRoot() {
  let tethys_app_root_url = process.env.TETHYS_APP_ROOT_URL;
  let tethys_prefix_url = process.env.TETHYS_PREFIX_URL.replace(/^\/|\/$/g, "");
  let fp = `/${tethys_prefix_url}/${tethys_app_root_url}`;
  return fp.replace(/\/{2,}/g, "/");
}
