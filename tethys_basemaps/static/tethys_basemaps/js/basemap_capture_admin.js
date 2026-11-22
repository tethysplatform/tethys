/*****************************************************************************
 * FILE:    basemap_capture_admin.js
 * DATE:    November 2026
 * AUTHOR:  Jacob Johnson
 * COPYRIGHT: (c) Aquaveo 2026
 *****************************************************************************/
$(function () {
  "use strict";

  const urls = JSON.parse(document.getElementById("capture-urls").textContent);
  const map = TETHYS_MAP_VIEW.getMap();

  const postAction = (url, failureMessage) =>
    fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: { "X-CSRFToken": get_csrf_token() },
    }).then((response) => {
      if (response.ok || response.status === 409) {
        window.location.reload();
        return;
      }
      return response.text().then((text) => {
        throw new Error(text || `${failureMessage} (HTTP ${response.status}).`);
      });
    });

  const message = document.getElementById("capture-message");
  const showMessage = (text, isError = false) => {
    message.textContent = text;
    message.style.color = isError ? "var(--error-fg)" : "";
    message.hidden = false;
  };

  setUpBasemapDropdown();
  if (urls.status) { setUpProgress(); }
  if (urls.restart) { setUpRestart(); }
  setUpAddPage();

  // OpenLayers stops clicks inside map controls from Bootstrap detecting,
  // so toggle the basemap dropdown directly.
  function setUpBasemapDropdown() {
    const container = document.getElementById("basemap_dropdown_container");
    if (!container) { return; }
    const toggle = document.getElementById("basemap_dropdown");
    container.addEventListener("click", (e) => {
      if (e.target.closest("#basemap_dropdown")) {
        bootstrap.Dropdown.getOrCreateInstance(toggle).toggle();
      } else if (e.target.closest(".basemap-option")) {
        bootstrap.Dropdown.getOrCreateInstance(toggle).hide();
      }
    });
  }

  function setUpProgress() {
    showMessage("Processing… You can leave this page; the capture keeps running.");

    if (urls.cancel) {
      const cancelButton = document.createElement("input");
      cancelButton.type = "button";
      cancelButton.className = "button";
      cancelButton.value = "Cancel capture";
      cancelButton.style.marginLeft = "1em";
      message.after(cancelButton);

      cancelButton.addEventListener("click", () => {
        if (!window.confirm("Stop this capture? The tiles downloaded so far will be discarded.")) {
          return;
        }
        cancelButton.disabled = true;
        cancelButton.value = "Cancelling…";
        postAction(urls.cancel, "The capture could not be cancelled").catch((error) => {
          cancelButton.disabled = false;
          cancelButton.value = "Cancel capture";
          showMessage(error.message, true);
        });
      });
    }

    const report = BASEMAP_CAPTURE.progressReporter();
    BASEMAP_CAPTURE.waitForCapture(
      { status: "processing", status_url: urls.status },
      (s) => { showMessage(`${report(s)} You can leave this page; it keeps running.`); }
    )
      // reload so the status and error fields are current
      .then(() => window.location.reload())
      .catch((error) => {
        if (error instanceof TypeError || /could not check/i.test(error.message)) {
          showMessage(error.message, true);
        } else {
          window.location.reload();
        }
      });
  }

  function setUpRestart() {
    showMessage("This capture was cancelled. Restart it to download it again from the start.");
    const restartButton = document.createElement("input");
    restartButton.type = "button";
    restartButton.className = "button default";
    restartButton.value = "Restart capture";
    restartButton.style.marginLeft = "1em";
    message.after(restartButton);

    restartButton.addEventListener("click", () => {
      restartButton.disabled = true;
      restartButton.value = "Restarting…";
      postAction(urls.restart, "The capture could not be restarted").catch((error) => {
        restartButton.disabled = false;
        restartButton.value = "Restart capture";
        showMessage(error.message, true);
      });
    });
  }

  // Add page only (on the change page, min_zoom is read-only text)
  function setUpAddPage() {
    const form = document.getElementById("basemapcapture_form");
    const minZoom = document.getElementById("id_min_zoom");
    if (!form || !minZoom) { return; }

    const maxZoom = document.getElementById("id_max_zoom");
    const nameInput = document.getElementById("id_name");
    const geometry = document.getElementById("map_view_geometry");
    const rateInput = document.getElementById("id_max_requests_per_second");
    const daskSchedulerInput = document.getElementById("id_dask_scheduler");
    const rateRow = form.querySelector(".field-max_requests_per_second");
    const buttons = form.querySelectorAll(".submit-row input[type=submit]");
    const KEEP_OPEN = " Keep this page open until it finishes.";
    let busy = false;

    const getRate = () => (rateInput && rateInput.value ? Number(rateInput.value) : null);
    const onServer = () => !!(daskSchedulerInput && daskSchedulerInput.value);

    // Protect against leaving the page while a capture is in progress in the browser
    const guardLeave = (e) => { e.preventDefault(); e.returnValue = ""; };
    const setLeaveGuard = (on) => {
      if (on) { window.addEventListener("beforeunload", guardLeave); }
      else { window.removeEventListener("beforeunload", guardLeave); }
    };

    // Min zoom follows the map's zoom
    const syncMinZoom = () => { minZoom.value = Math.floor(map.getView().getZoom()); };
    map.on("moveend", syncMinZoom);
    syncMinZoom();

    // Status line above the Save buttons
    const status = document.createElement("p");
    status.id = "capture-status";
    status.className = "help";
    form.querySelector(".submit-row").before(status);
    const showStatus = (text, isError = false) => {
      status.textContent = text;
      status.style.color = isError ? "var(--error-fg)" : "";
    };

    // EPSG:3857 extent: the drawn box if there is one, otherwise the visible map
    const getCaptureExtent = () => {
      const geometries = geometry && geometry.value ? JSON.parse(geometry.value).geometries || [] : [];
      if (geometries.length === 0) {
        return map.getView().calculateExtent(map.getSize());
      }
      if (geometries.length !== 1 || geometries[0].type !== "Polygon") {
        throw new Error("Draw at most one capture area. Use the delete tool to remove extras.");
      }
      const ring = geometries[0].coordinates[0];
      const lons = ring.map((p) => p[0]);
      const lats = ring.map((p) => p[1]);
      return ol.proj.transformExtent(
        [Math.min(...lons), Math.min(...lats), Math.max(...lons), Math.max(...lats)],
        "EPSG:4326",
        "EPSG:3857"
      );
    };

    // Before saving, the status line shows the tile count and a time estimate
    const updateEstimate = () => {
       // the rate only applies to server downloads
      if (rateRow) { rateRow.hidden = !onServer(); } 
      // don't overwrite progress
      if (busy) { return; }                          

      const basemap = BASEMAP_CAPTURE.getCurrentBasemap(map);
      if (!basemap) { showStatus(""); return; }
      let extent;
      try { extent = getCaptureExtent(); } catch (error) { showStatus(error.message, true); return; }

      const plan = BASEMAP_CAPTURE.getPlan(
        basemap, extent, parseInt(minZoom.value, 10), parseInt(maxZoom.value, 10)
      );
      if (plan.error) { showStatus(plan.error, true); return; }
      showStatus(BASEMAP_CAPTURE.describePlan(plan.count, { onServer: onServer(), rate: getRate() }));
    };

    // rendercomplete covers panning, zooming, switching basemaps and drawing a box
    map.on("rendercomplete", updateEstimate);
    [maxZoom, rateInput].forEach((el) => el && el.addEventListener("input", updateEstimate));
    if (daskSchedulerInput) { daskSchedulerInput.addEventListener("change", updateEstimate); }
    updateEstimate();

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      if (busy) { return; }

      const submitter = e.submitter ? e.submitter.name : "_save";
      const name = nameInput.value.trim();
      if (!name) {
        showStatus("Enter a name for the capture.", true);
        return;
      }

      let extent;
      try {
        extent = getCaptureExtent();
      } catch (error) {
        showStatus(error.message, true);
        return;
      }

      const daskScheduler = daskSchedulerInput ? daskSchedulerInput.value : "";
      const zooms = {
        minZoom: parseInt(minZoom.value, 10),
        maxZoom: parseInt(maxZoom.value, 10),
      };

      const browserCapture = () => BASEMAP_CAPTURE.capture({
        map, extent, name, ...zooms,
        csrfToken: get_csrf_token(),
        uploadUrl: urls.upload,
        onProgress: (done, total) => {
          showStatus(`Fetching tiles: ${done.toLocaleString()} / ${total.toLocaleString()}.${KEEP_OPEN}`);
        },
        onUploading: (count) => {
          showStatus(`Uploading and processing ${count.toLocaleString()} tiles…` + KEEP_OPEN);
        },
      });

      busy = true;
      setLeaveGuard(true);
      buttons.forEach((b) => { b.disabled = true; });

      let job;
      if (daskScheduler) {
        showStatus("Starting the download on the server…");
        job = BASEMAP_CAPTURE.startServerCapture({
          map, extent, name, ...zooms, daskScheduler,
          maxRequestsPerSecond: getRate(),
          serverUrl: urls.server,
          csrfToken: get_csrf_token(),
        }).catch((error) => {
          if (!error.browserOnly) { throw error; }
          // The server can't download this basemap (e.g. a built-in one); 
          // fetch it in the browser instead
          showStatus(`${error.message} Downloading in the browser instead…`);
          return browserCapture();
        });
      } else {
        showStatus("Starting…");
        job = browserCapture();
      }

      job
        .then((result) => {
          setLeaveGuard(false);
          if (result.status === "failed") {
            throw new Error(result.error || "The capture could not be built.");
          }
          if (submitter === "_addanother") {
            window.location.reload();
          } else if (submitter === "_continue" || result.status === "processing") {
            // A processing capture's change page shows its progress
            window.location.href = result.change_url;
          } else {
            window.location.href = result.basemap_capture_list_url;
          }
        })
        .catch((error) => {
          setLeaveGuard(false);
          busy = false;
          buttons.forEach((b) => { b.disabled = false; });
          showStatus(error.message || "The capture could not be saved.", true);
        });
    });
  }
});