/*****************************************************************************
 * FILE:    basemap_upload_image.js
 * DATE:    November 2026
 * AUTHOR:  Jacob Johnson
 * COPYRIGHT: (c) Aquaveo 2026
 *****************************************************************************/

(function () {
  "use strict";

  const mapContainer = document.getElementById("basemap-image-map");
  // The inline formset of the basemap's images (BasemapImageSource rows)
  const FORMSET = "sources";

  // Minimum border for an overlay image on the map for height or width
  const MIN_BORDER = 1;
  // Outline colors, so each box on the map can be differentiated
  const COLORS = ["#ff0", "#0ff", "#f0f", "#f80", "#0f0", "#08f", "#f44", "#fff"];
  // Overlay data for the current basemap image: its saved sources and finished mosaic
  const overlayData = JSON.parse(document.getElementById("basemap-image-overlay").textContent);

  if (!mapContainer) { return; }

  // TODO we may want to change this from using open street
  // maps to use a local basemap that's already been uploaded
  // since these uploads are meant to be able to work offline too
  const map = new ol.Map({
    target: mapContainer,
    layers: [new ol.layer.Tile({ source: new ol.source.OSM() })],
    view: new ol.View({ center: ol.proj.fromLonLat([0, 20]), zoom: 2 }),
  });

  const urls = JSON.parse(document.getElementById("basemap-image-urls").textContent);
  const processingNote = document.getElementById("basemap-image-processing");


  if (urls.cancel && processingNote) {
    const cancelButton = document.createElement("input");
    cancelButton.type = "button";
    cancelButton.className = "button";
    cancelButton.value = "Cancel processing";
    cancelButton.style.marginLeft = "1em";
    processingNote.append(cancelButton);

    cancelButton.addEventListener("click", () => {
      if (!window.confirm("Stop processing this image? Save it again later to process it.")) {
        return;
      }
      cancelButton.disabled = true;
      cancelButton.value = "Cancelling…";
      fetch(urls.cancel, {
        method: "POST",
        credentials: "same-origin",
        headers: { "X-CSRFToken": get_csrf_token() },
      })
        .then((response) => {
          // 409 means it finished before the cancel landed
          if (response.ok || response.status === 409) {
            window.location.reload();
            return;
          }
          return response.text().then((text) => {
            throw new Error(text || `The image could not be cancelled (HTTP ${response.status}).`);
          });
        })
        .catch((error) => {
          cancelButton.disabled = false;
          cancelButton.value = "Cancel processing";
          window.alert(error.message);
        });
    });
  }
  if (urls.status) {
    const poll = setInterval(() => {
      fetch(urls.status, { credentials: "same-origin" })
        .then((response) => (response.ok ? response.json() : null))
        .then((data) => {
          if (data && data.status !== "processing") {
            clearInterval(poll);
            window.location.reload();  // Reload the page to show results
          }
        })
        // Ignore errors, let the next poll try again
        .catch(() => {});
    }, 3000);
  }

  // The finished mosaic, under the adjustable overlays, so the white fill shows too
  if (overlayData.tile_url) {
    const mosaicOptions = {
      source: new ol.source.XYZ({ url: overlayData.tile_url }),
      opacity: 0.6,
      zIndex: 1,
    };
    if (overlayData.bounds) { mosaicOptions.extent = overlayData.bounds; }
    map.addLayer(new ol.layer.Tile(mosaicOptions));
  }

  // One entry per inline row, with the row element as the key
  const rows = new Map();
  let colorCount = 0;

  function rowInput(row, suffix) {
    return row.querySelector(`[name^="${FORMSET}-"][name$="-${suffix}"]`);
  }

  function rowOrder(row) {
    const input = rowInput(row, "order");
    const value = input ? parseInt(input.value, 10) : 0;
    return Number.isNaN(value) ? 0 : value;
  }

  // After a vertex drag, keep the box axis-aligned: anchor the opposite corner
  function resizeFromDrag(feature, pre) {
    if (!pre) { return feature.getGeometry().getExtent(); }

    // The box's corners before and after the drag, in the same order
    const oldCorners = ol.geom.Polygon.fromExtent(pre).getCoordinates()[0];
    const newCorners = feature.getGeometry().getCoordinates()[0];

    // Only one corner can be dragged, so it's the one that changed.
    // The ring's 5th point repeats the 1st, so only the first 4 are corners.
    const movedIdx = newCorners.findIndex((pt, i) =>
      i < 4 && (pt[0] !== oldCorners[i][0] || pt[1] !== oldCorners[i][1])
    );
    if (movedIdx < 0) { return pre; }

    const moved = newCorners[movedIdx];
    const anchor = oldCorners[(movedIdx + 2) % 4];
    const next = ol.extent.boundingExtent([moved, anchor]);

    if (next[2] - next[0] < MIN_BORDER || next[3] - next[1] < MIN_BORDER) { return pre; }
    return next;
  }

  function writeGeoreference(state, extent) {
    const input = rowInput(state.row, "georeference");
    if (input) {
      input.value = extent ? JSON.stringify({ epsg: 3857, bounds: extent }) : "";
    }
  }

  // Higher order draws on top; each row's outline sits just above its image
  function applyOrder(state) {
    const z = 10 + rowOrder(state.row) * 2;
    if (state.imageLayer) { state.imageLayer.setZIndex(z); }
    if (state.boxLayer) { state.boxLayer.setZIndex(z + 1); }
  }

  function clearOverlay(state) {
    [state.imageLayer, state.boxLayer].forEach((layer) => layer && map.removeLayer(layer));
    state.interactions.forEach((interaction) => map.removeInteraction(interaction));
    if (state.objectUrl) { URL.revokeObjectURL(state.objectUrl); }
    state.imageLayer = null;
    state.boxLayer = null;
    state.interactions = [];
    state.objectUrl = null;
  }

  function setVisible(state, visible) {
    [state.imageLayer, state.boxLayer].forEach((layer) => layer && layer.setVisible(visible));
    state.interactions.forEach((interaction) => interaction.setActive(visible));
  }

  // A box for the row's image. Without a url (ex: a GeoTIFF shown by the mosaic tiles),
  // only the outline is drawn and it can't be moved.
  function addOverlay(state, url, extent, writeInput) {
    clearOverlay(state);
    const color = state.color;

    if (url) {
      state.imageLayer = new ol.layer.Image({
        source: new ol.source.ImageStatic({ url, imageExtent: extent, projection: "EPSG:3857" }),
        opacity: 0.7,
      });
      map.addLayer(state.imageLayer);
    }

    const feature = new ol.Feature(ol.geom.Polygon.fromExtent(extent));
    const vectorSource = new ol.source.Vector({ features: [feature] });
    state.boxLayer = new ol.layer.Vector({
      source: vectorSource,
      style: new ol.style.Style({
        stroke: new ol.style.Stroke({ color, width: 2, lineDash: url ? undefined : [6, 4] }),
        fill: new ol.style.Fill({ color: "rgba(255,255,255,0.05)" }),
      }),
    });
    map.addLayer(state.boxLayer);
    applyOrder(state);

    if (writeInput) { writeGeoreference(state, extent); }
    if (!url) { return; }

    const translate = new ol.interaction.Translate({ features: new ol.Collection([feature]) });
    const modify = new ol.interaction.Modify({
      source: vectorSource,
      insertVertexCondition: ol.events.condition.never,
    });

    let preExtent = null;

    function applyExtent(e) {
      feature.getGeometry().setCoordinates(ol.geom.Polygon.fromExtent(e).getCoordinates());
      state.imageLayer.setSource(new ol.source.ImageStatic({ url, imageExtent: e, projection: "EPSG:3857" }));
      writeGeoreference(state, e);
    }

    translate.on("translateend", () => applyExtent(feature.getGeometry().getExtent().slice()));
    modify.on("modifystart", () => { preExtent = feature.getGeometry().getExtent().slice(); });
    modify.on("modifyend", () => applyExtent(resizeFromDrag(feature, preExtent)));

    map.addInteraction(translate);
    map.addInteraction(modify);
    state.interactions.push(translate, modify);
  }

  // A newly picked file: drop it at the center of the view, sized to ~400 screen pixels wide
  function placeImage(state, file) {
    const url = URL.createObjectURL(file);
    const probe = new Image();

    probe.onload = () => {
      const view = map.getView();
      const center = view.getCenter();
      const w = view.getResolution() * 400;
      const h = w * (probe.naturalHeight / probe.naturalWidth);
      addOverlay(state, url, [center[0] - w / 2, center[1] - h / 2, center[0] + w / 2, center[1] + h / 2], true);
      state.objectUrl = url;
    };

    probe.onerror = () => {
      // Not browser-viewable (e.g. GeoTIFF). Don't submit a stale placement for it;
      // if it has a coordinate system, the server places it on save.
      URL.revokeObjectURL(url);
      writeGeoreference(state, null);
    };

    probe.src = url;
  }

  function toMapExtent(source) {
    let extent = source.bounds;
    if (source.epsg && source.epsg !== 3857) {
      extent = ol.proj.transformExtent(extent, `EPSG:${source.epsg}`, "EPSG:3857");
    }
    return extent;
  }

  // Start tracking an inline row: its saved placement, and any file picked for it
  function registerRow(row, saved) {
    if (rows.has(row)) { return rows.get(row); }
    const state = {
      row,
      color: COLORS[colorCount++ % COLORS.length],
      imageLayer: null,
      boxLayer: null,
      interactions: [],
      objectUrl: null,
    };
    rows.set(row, state);

    // Match the row's color to its box on the map
    const fileInput = rowInput(row, "source_file");
    if (fileInput) {
      fileInput.style.borderLeft = `6px solid ${state.color}`;
      fileInput.addEventListener("change", () => {
        const file = fileInput.files[0];
        if (!file) { return; }
        clearOverlay(state);
        placeImage(state, file);
      });
    }

    const orderInput = rowInput(row, "order");
    if (orderInput) { orderInput.addEventListener("input", () => applyOrder(state)); }

    const deleteInput = rowInput(row, "DELETE");
    if (deleteInput) {
      deleteInput.addEventListener("change", () => setVisible(state, !deleteInput.checked));
    }

    if (saved && saved.bounds && saved.bounds.length === 4) {
      addOverlay(state, saved.image_url, toMapExtent(saved), false);
    }
    return state;
  }

  // Saved sources, matched to their rows by the inline's hidden id input
  const savedById = new Map(overlayData.sources.map((source) => [String(source.id), source]));
  const extents = [];
  document.querySelectorAll(`#${FORMSET}-group tr.form-row:not(.empty-form)`).forEach((row) => {
    const idInput = rowInput(row, "id");
    const saved = idInput ? savedById.get(idInput.value) : undefined;
    registerRow(row, saved);
    if (saved && saved.bounds && saved.bounds.length === 4) { extents.push(toMapExtent(saved)); }
  });
  if (overlayData.bounds) { extents.push(overlayData.bounds); }

  if (extents.length) {
    const all = extents.reduce((acc, e) => ol.extent.extend(acc, e), ol.extent.createEmpty());
    map.getView().fit(all, { padding: [40, 40, 40, 40] });
  }

  // Rows added with "Add another Image"
  document.addEventListener("formset:added", (event) => {
    if (event.detail && event.detail.formsetName === FORMSET) {
      registerRow(event.target, null);
    }
  });

  // An unsaved row was removed: drop the overlays of rows no longer on the page
  document.addEventListener("formset:removed", (event) => {
    if (!event.detail || event.detail.formsetName !== FORMSET) { return; }
    rows.forEach((state, row) => {
      if (!row.isConnected) {
        clearOverlay(state);
        rows.delete(row);
      }
    });
  });
})();
