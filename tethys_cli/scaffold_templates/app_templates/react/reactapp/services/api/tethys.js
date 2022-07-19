import apiClient from "services/api/client";

function getSession() {
  return apiClient.get('/api/session/');
}

function getCSRF() {
  return apiClient.get('/api/csrf/')
    .then(response => {
      return response.headers['x-csrftoken'];
    });
}

function getUserData() {
  return apiClient.get('/api/whoami/');
}

function getAppData(tethys_app_url) {
  return apiClient.get(`/api/apps/${tethys_app_url}/`);
}

const tethysAPI = {
  getSession,
  getCSRF,
  getAppData,
  getUserData,
};

export default tethysAPI;