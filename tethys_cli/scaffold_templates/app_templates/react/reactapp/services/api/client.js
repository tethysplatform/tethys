import axios from "axios";

import { getTethysPortalBase } from "services/utilities";

const TETHYS_PORTAL_BASE = getTethysPortalBase();

const apiClient = axios.create({
  baseURL: `${TETHYS_PORTAL_BASE}`,
  withCredentials: true,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
});

function handleSuccess(response) {
  return response.data ? response.data : response;
}

function handleError(error) {
  let res = error.response;
  if (res.status === 401) {
    // Redirect to Tethys Portal login
    window.location.assign(
      `${TETHYS_PORTAL_BASE}/accounts/login?next=${window.location.pathname}`
    );
  }
  return Promise.reject(error);
}

apiClient.interceptors.response.use(handleSuccess, handleError);

export default apiClient;
