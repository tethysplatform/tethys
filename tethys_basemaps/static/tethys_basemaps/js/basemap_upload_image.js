/*****************************************************************************
 * FILE:    basemap_upload_image.js
 * DATE:    November 2026
 * AUTHOR:  Jacob Johnson
 * COPYRIGHT: (c) Aquaveo 2026
 *****************************************************************************/

(function () {
  "use strict";

  const mapContainer = document.getElementById("basemap-image-map");
  const fileInput = document.getElementById("id_source_file");
  const georefInput = document.getElementById("id_georeference");

  // Minimum border for the overlay image on the map for height or width
  const MIN_BORDER = 1; 
  // Overlay image data for the current basemap image
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

    function csrfToken() {
      const input = document.querySelector("[name=csrfmiddlewaretoken]");
      return input ? input.value : "";
    }

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
          headers: { "X-CSRFToken": csrfToken() },
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
  // Everything added for the current image, so picking a new file starts clean
  let overlayLayers = [];
  let overlayInteractions = [];

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

  function writeGeoreference(extent) {
    if (georefInput) {
      georefInput.value = JSON.stringify({ epsg: 3857, bounds: extent });
    }
  }

  function clearOverlay() {
    overlayLayers.forEach((layer) => map.removeLayer(layer));
    overlayInteractions.forEach((interaction) => map.removeInteraction(interaction));
    overlayLayers = [];
    overlayInteractions = [];
  }

  function addOverlay(url, extent, writeInput) {
    const layer = new ol.layer.Image({
      source: new ol.source.ImageStatic({ url, imageExtent: extent, projection: "EPSG:3857" }),
      opacity: 0.7,
    });

    const feature = new ol.Feature(ol.geom.Polygon.fromExtent(extent));
    const vectorSource = new ol.source.Vector({ features: [feature] });
    const vectorLayer = new ol.layer.Vector({
      source: vectorSource,
      style: new ol.style.Style({
        stroke: new ol.style.Stroke({ color: "#ff0", width: 2 }),
        fill: new ol.style.Fill({ color: "rgba(255,255,0,0.05)" }),
      }),
    });

    map.addLayer(layer);
    map.addLayer(vectorLayer);
    overlayLayers.push(layer, vectorLayer);

    if (writeInput) { writeGeoreference(extent); }

    const translate = new ol.interaction.Translate({ features: new ol.Collection([feature]) });
    const modify = new ol.interaction.Modify({
      source: vectorSource,
      insertVertexCondition: ol.events.condition.never,
    });

    let preExtent = null;

    function applyExtent(e) {
      feature.getGeometry().setCoordinates(ol.geom.Polygon.fromExtent(e).getCoordinates());
      layer.setSource(new ol.source.ImageStatic({ url, imageExtent: e, projection: "EPSG:3857" }));
      writeGeoreference(e);
    }

    translate.on("translateend", () => applyExtent(feature.getGeometry().getExtent().slice()));
    modify.on("modifystart", () => { preExtent = feature.getGeometry().getExtent().slice();  });
    modify.on("modifyend", () => applyExtent(resizeFromDrag(feature, preExtent)));

    map.addInteraction(translate);
    map.addInteraction(modify);
    overlayInteractions.push(translate, modify);  
  }

  // A newly picked file: drop it at the center of the view, sized to ~400 screen pixels wide
  function placeImage(file) {
    const url = URL.createObjectURL(file);
    const probe = new Image();

    probe.onload = () => {
      const view = map.getView();
      const center = view.getCenter();
      const w = view.getResolution() * 400;
      const h = w * (probe.naturalHeight / probe.naturalWidth);
      addOverlay(url, [center[0] - w / 2, center[1] - h / 2, center[0] + w / 2, center[1] + h / 2], true);
    };

    probe.onerror = () => {
      // Not browser-viewable (e.g. GeoTIFF). Don't submit a stale placement for it;
      // if it has a coordinate system, the server places it on save.
      URL.revokeObjectURL(url);
      if (georefInput) { georefInput.value = ""; }
    };

    probe.src = url;
  }

  // Use when editing to show the saved placement (adjustable preview) or the image's tiles
  if (overlayData.bounds && overlayData.bounds.length === 4) {
    let extent = overlayData.bounds;
    if (overlayData.epsg && overlayData.epsg !== 3857) {
      extent = ol.proj.transformExtent(extent, `EPSG:${overlayData.epsg}`, "EPSG:3857");
    }

    if (overlayData.image_url) {
      addOverlay(overlayData.image_url, extent, false);
    } else if (overlayData.tile_url) {
      map.addLayer(new ol.layer.Tile({
        source: new ol.source.XYZ({ url: overlayData.tile_url }),
        extent,
      }));
    }
    map.getView().fit(extent, { padding: [40, 40, 40, 40] });
  }

  if (fileInput) {
    fileInput.addEventListener("change", () => {
      const file = fileInput.files[0];
      if (!file) { return; }
      clearOverlay();
      placeImage(file);
    });
  }
})();