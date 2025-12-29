import apiClient from "services/api/client";

// JWT token storage helpers
const ACCESS_TOKEN_KEY = "jwt_access";
const REFRESH_TOKEN_KEY = "jwt_refresh";

export function setTokens(access, refresh) {
  localStorage.setItem(ACCESS_TOKEN_KEY, access);
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
}
export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}
export function getRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

async function getJWTToken() {
  const response = await apiClient.get("/api/token/", {});
  const access = response.access;
  const refresh = response.refresh;
  setTokens(access, refresh);
  return { access, refresh };
}

async function refreshJWTToken() {
  const response = await apiClient.post("/api/token/refresh/", {
    refresh: getRefreshToken(),
  });
  return response.data.access;
}

function getUserData() {
  return apiClient.get("/api/whoami/");
}

function getAppData(tethys_app_url) {
  return apiClient.get(`/api/apps/${tethys_app_url}/`);
}

const tethysAPI = {
  getJWTToken,
  refreshJWTToken,
  getAppData,
  getUserData,
};

export default tethysAPI;
