'use strict';
(function () {
  let DISCONNECTED = false;
  let INTERVAL = null;
  const progressBar = document.querySelector('#progress');
  const doNotLeave = document.querySelector('#do-not-leave');
  const message = document.querySelector('#message');
  const appLifeCycleSocket = new ReconnectingWebSocket(
    'ws://'
    + window.location.host
    + '/ws/app-lifecycle/'
    + PROJECT_NAME
    + '/'
  );
  let APP_PACKAGE = PROJECT_NAME;
  
  appLifeCycleSocket.onopen = function(e) {
    if (DISCONNECTED) {
      updateProgress({message: "Done", percentage: 100});
      let redirectUrl = window.location.protocol + "//" + window.location.host + '/apps/';
      if (APP_LIFECYCLE_ACTION != "Removing") {
        redirectUrl += APP_PACKAGE.replaceAll("_", "-") + "/"
      }
      window.location.assign(redirectUrl);
    }
  };
  
  appLifeCycleSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.app_package) {
      APP_PACKAGE = data.app_package;
    }
    if (data.error_code) {
      reportError(data);
    } else {
      updateProgress(data);
    }
  };
  
  appLifeCycleSocket.onclose = function(e) {
    DISCONNECTED = true;
  };

  function reportError(data) {
    progressBar.style.display = 'none';
    doNotLeave.style.display = 'none';
    message.innerHTML = 'ERROR ENCOUNTERED: ' + data.message;
  }
  
  function updateProgress(data) {
    if (parseInt(data.percentage) > parseInt(progressBar.ariaValueNow)) {
      progressBar.ariaValueNow = data.percentage;
      progressBar.style['width'] = data.percentage + '%';
    }
    if (data.message) {
      message.innerHTML = data.message;
    }
  }

  INTERVAL = window.setInterval(function () {
    if (parseInt(progressBar.ariaValueNow) < 98) {
      updateProgress({percentage: parseInt(progressBar.ariaValueNow) + 1});
    } else {
      window.clearInterval(INTERVAL);
      progressBar.classList.add("progress-bar-animated");
    }
  }, 1500);
}())