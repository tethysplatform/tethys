/*****************************************************************************
 * FILE:    tethys_map_view_capture_control.js
 * DATE:    November 2026
 * AUTHOR:  Jacob Johnson
 * COPYRIGHT: (c) Aquaveo 2026
 *****************************************************************************/
const BASEMAP_CAPTURE_CONTROL = (function () {
  "use strict";

  const DEFAULT_MAX_ZOOM = 24;
  const BASEMAP_PREFIX = "Basemap: ";   // Prefix used in tethys_legend_title for basemap layers

  let map = null;
  let modalElement = null;
  let drawing = null;      // Stores the current drawing state: { box, paused, onKey } while the user is drawing
  let drawnExtent = null;  // the drawn box or null for the visible area
  let keepFields = false;  // Keeps the input fields the same while the modal is closed for drawing
  let areaLayer = null;
  let drawingHint = null;
  let runningCapture = false;
  const KEEP_OPEN_MESSAGE = " Keep this page open until it finishes.";
  const warnBeforeLeaving = (e) => { e.preventDefault(); e.returnValue = ""; };

  // Label of the visible basemap
  function getCurrentBasemapLabel() {
    const layer = map.getLayers().getArray().find((l) =>
      typeof l.tethys_legend_title === "string" &&
      l.tethys_legend_title.startsWith(BASEMAP_PREFIX) &&
      l.getVisible()
    );
    return layer ? layer.tethys_legend_title.slice(BASEMAP_PREFIX.length) : null;
  }

  // Get or create the vector source for the drawn area layer
  function areaSource() {
    if (!areaLayer) {
      areaLayer = new ol.layer.Vector({
        source: new ol.source.Vector(),
        style: new ol.style.Style({
          stroke: new ol.style.Stroke({ color: "#0d6efd", width: 2, lineDash: [6, 4] }),
          fill: new ol.style.Fill({ color: "rgba(13, 110, 253, 0.1)" }),
        }),
      });
      areaLayer.setMap(map);
    }
    return areaLayer.getSource();
  }

  // Set the drawn area and update the UI
  function setArea(extent) {
    drawnExtent = extent;
    const source = areaSource();
    source.clear();
    if (extent) { source.addFeature(new ol.Feature(ol.geom.Polygon.fromExtent(extent))); }
    document.getElementById("basemap-capture-area").textContent = extent ? "Drawn area" : "Visible map area";
    document.getElementById("basemap-capture-clear").hidden = !extent;
    updateEstimate();
  }

  // What Save will capture: the drawn box, or what the map shows
  function captureExtent() {
    return drawnExtent || map.getView().calculateExtent(map.getSize());
  }

  // Show or hide the drawing hint that appears while drawing the capture area
  function showDrawingHint(show) {
    if (!drawingHint) {
      drawingHint = document.createElement("div");
      drawingHint.className = "basemap-capture-hint";
      drawingHint.textContent = "Drag to draw the capture area · Esc to cancel";
      map.getTargetElement().appendChild(drawingHint);
    }
    drawingHint.hidden = !show;
  }

  // Start drawing the capture area
  function startDraw() {
    // Make sure the modal's inputs don't reset while the modal is hidden
    keepFields = true;
    bootstrap.Modal.getOrCreateInstance(modalElement).hide();

    // Stop panning and other interactions except for zooming
    const paused = map.getInteractions().getArray().filter((i) =>
      i.getActive() && !(i instanceof ol.interaction.MouseWheelZoom));
    paused.forEach((i) => i.setActive(false));

    const box = new ol.interaction.DragBox();
    box.on("boxend", () => endDraw(box.getGeometry().getExtent()));
    map.addInteraction(box);

    const onKey = (e) => { if (e.key === "Escape") { endDraw(null); } };
    document.addEventListener("keydown", onKey);

    map.getTargetElement().style.cursor = "crosshair";
    showDrawingHint(true);
    drawing = { box, paused, onKey };
  }

  // Stop drawing the capture area
  function endDraw(extent) {
    if (!drawing) { return; }
    map.removeInteraction(drawing.box);
    drawing.paused.forEach((i) => i.setActive(true));
    document.removeEventListener("keydown", drawing.onKey);
    map.getTargetElement().style.cursor = "";
    showDrawingHint(false);
    drawing = null;
    if (extent) { setArea(extent); }
    open();
  }

  // Populate the modal's fields with the current map state (basemap and zoom)
  function onShow() {
    if (keepFields) { keepFields = false; updateEstimate(); return; }   // back from drawing
    const zoom = Math.max(0, Math.floor(map.getView().getZoom()));
    const label = getCurrentBasemapLabel();
    document.getElementById("basemap-capture-basemap").textContent = label || "the current basemap";
    document.getElementById("basemap-capture-min-zoom").value = Math.min(zoom, DEFAULT_MAX_ZOOM);
    document.getElementById("basemap-capture-max-zoom").value = Math.min(zoom + 2, DEFAULT_MAX_ZOOM);
    updateEstimate();
  }

  function open() {
    if (modalElement) { bootstrap.Modal.getOrCreateInstance(modalElement).show(); }
  }

  // Place the capture button in the basemap picker container if it exists
  function placeButton() {
    const button = document.getElementById("basemap-capture-button");
    if (!button) { return; }
    button.addEventListener("click", open);

    const toggle = document.getElementById("basemap_dropdown");
    const container = document.getElementById("basemap_dropdown_container");
    if (!toggle || !container) { return; }  

    button.className = toggle.className.replace(/\bdropdown-toggle\b/g, "").trim();
    container.appendChild(button);
  }

  // Show a status message in the modal
  function showStatus(text, isError = false) {
    const el = document.getElementById("basemap-capture-status");
    el.textContent = text;
    el.classList.toggle("text-danger", isError);
  }

  // Show the progress bar in the modal
  function showProgress(done, total) {
    const row = document.getElementById("basemap-capture-progress");
    row.hidden = false;
    row.firstElementChild.style.width = `${total ? Math.floor((100 * done) / total) : 0}%`;
  }

  // Determine whether to download on the server or not
  function onServer() {
    const box = document.getElementById("basemap-capture-download-type");
    const scheduler = document.getElementById("basemap-capture-scheduler");
    return !!(box && box.checked && scheduler && scheduler.value);
  }

  function zooms() {
    return {
      minZoom: parseInt(document.getElementById("basemap-capture-min-zoom").value, 10),
      maxZoom: parseInt(document.getElementById("basemap-capture-max-zoom").value, 10),
    };
  }

  // Get the max requests per second for a server download, or null for the server's default
  function maxRate() {
    const input = document.getElementById("basemap-capture-rate");
    const value = input && input.value ? parseInt(input.value, 10) : null;
    return Number.isInteger(value) && value > 0 ? value : null;
  }

  // Show tile count and time estimate, or why it can't be captured
  function updateEstimate() {
    if (runningCapture) { return; }   // don't overwrite progress
    const save = document.getElementById("basemap-capture-save");
    const rateInput = document.getElementById("basemap-capture-rate");
    if (onServer() && rateInput && rateInput.value && !rateInput.checkValidity()) {
      showStatus(`Max requests per second must be between 1 and ${rateInput.max}.`, true);
      save.disabled = true;
      return;
    }
    const basemap = BASEMAP_CAPTURE.getCurrentBasemap(map);
    if (!basemap) {
      showStatus("Choose a basemap in the basemap menu first.", true);
      save.disabled = true;
      return;
    }
    const { minZoom, maxZoom } = zooms();
    const plan = BASEMAP_CAPTURE.getPlan(basemap, captureExtent(), minZoom, maxZoom);
    if (plan.error) {
      showStatus(plan.error, true);
      save.disabled = true;
      return;
    }
    showStatus(BASEMAP_CAPTURE.describePlan(plan.count, { onServer: onServer(), rate: onServer() ? maxRate() : null }));
    save.disabled = !document.getElementById("basemap-capture-name").value.trim();
  }

  function setRunningCapture(on) {
    runningCapture = on;
    ["basemap-capture-name", "basemap-capture-min-zoom", "basemap-capture-max-zoom",
     "basemap-capture-download-type", "basemap-capture-scheduler",
     "basemap-capture-draw", "basemap-capture-clear", "basemap-capture-save", "basemap-capture-rate"]
      .forEach((id) => { const el = document.getElementById(id); if (el) { el.disabled = on; } });
  }

  // Save the capture, either on the server or in the browser
  function save() {
    if (runningCapture) { return; }
    const name = document.getElementById("basemap-capture-name").value.trim();
    if (!name) { showStatus("Enter a name for the capture.", true); return; }

    const urls = modalElement.dataset;
    const common = { map, extent: captureExtent(), name, ...zooms(), csrfToken: get_csrf_token(), app: urls.app };

    // Capture tiles in the browser
    const browserCapture = () => {
      window.addEventListener("beforeunload", warnBeforeLeaving);
      return BASEMAP_CAPTURE.capture({
        ...common,
        uploadUrl: urls.uploadUrl,
        onProgress: (done, total) => {
          showProgress(done, total);
          showStatus(`Fetching tiles: ${done.toLocaleString()} / ${total.toLocaleString()}.${KEEP_OPEN_MESSAGE}`);
        },
        onUploading: (count) => {
          showStatus(`Uploading and processing ${count.toLocaleString()} tiles…${KEEP_OPEN_MESSAGE}`);
        },
      }).finally(() => window.removeEventListener("beforeunload", warnBeforeLeaving));
    };

    setRunningCapture(true);
    let job;
    if (onServer()) {
      showStatus("Starting the download on the server…");
      job = BASEMAP_CAPTURE.startServerCapture({
        ...common,
        daskScheduler: document.getElementById("basemap-capture-scheduler").value,
        maxRequestsPerSecond: maxRate(),
        serverUrl: urls.serverUrl,
      }).catch((error) => {
        if (!error.browserOnly) { throw error; }
        showStatus(`${error.message} Downloading in the browser instead…`);
        return browserCapture();
      });
    } else {
      showStatus("Starting…");
      job = browserCapture();
    }

    const report = BASEMAP_CAPTURE.progressReporter();
    job
      .then((result) => {
        if (result.status === "failed") {
          throw new Error(result.error || "The capture could not be built.");
        }
        return BASEMAP_CAPTURE.waitForCapture(result, (s) => {
          if (s.total) { showProgress(s.done, s.total); }
          showStatus(report(s));
        });
      })
      .then((result) => {
        setRunningCapture(false);
        if (result.status === "cancelled") { showStatus("The capture was cancelled."); return; }
        showProgress(1, 1);
        showStatus(`Saved "${result.name}". Reload the page to use it as a basemap.`);
      })
      .catch((error) => {
        setRunningCapture(false);
        showStatus((error && error.message) || "The capture could not be saved.", true);
      });
  }

  $(function () {
    const mapElement = document.getElementById("map_view");
    modalElement = document.getElementById("basemap-capture-modal");

    const downloadType = document.getElementById("basemap-capture-download-type");
    const scheduler = document.getElementById("basemap-capture-scheduler");
    
    if (downloadType && scheduler) {
      downloadType.addEventListener("change", (e) => {
        scheduler.parentElement.style.display = e.target.checked ? "block" : "none";
      });
    }
    if (!mapElement || !modalElement || typeof TETHYS_MAP_VIEW === "undefined") { return; }
    if (!$(mapElement).data("basemap-capture")) { return; }

    document.body.appendChild(modalElement);

    map = TETHYS_MAP_VIEW.getMap();
    modalElement.addEventListener("show.bs.modal", onShow);
    // If the modal is closed and we're not currently drawing, clear the drawn box.
    modalElement.addEventListener("hidden.bs.modal", () => { if (!drawing) { setArea(null); } });
    document.getElementById("basemap-capture-draw").addEventListener("click", startDraw);
    document.getElementById("basemap-capture-clear").addEventListener("click", () => setArea(null));
    ["basemap-capture-name", "basemap-capture-min-zoom", "basemap-capture-max-zoom"]
      .forEach((id) => document.getElementById(id).addEventListener("input", updateEstimate));
    ["basemap-capture-download-type", "basemap-capture-scheduler"]
      .forEach((id) => { const el = document.getElementById(id); if (el) { el.addEventListener("change", updateEstimate); } });
    document.getElementById("basemap-capture-save").addEventListener("click", save);
    const rateInput = document.getElementById("basemap-capture-rate");
    if (rateInput) { rateInput.addEventListener("input", updateEstimate); }
    placeButton();
  });

  // Use BASEMAP_CAPTURE_CONTROL.open() to manually open this modal
  return { open };
})();