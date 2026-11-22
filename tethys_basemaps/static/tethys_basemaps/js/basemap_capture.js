/*****************************************************************************
 * FILE:    basemap_capture.js
 * DATE:    November 2026
 * AUTHOR:  Jacob Johnson
 * COPYRIGHT: (c) Aquaveo 2026
 *****************************************************************************/
const BASEMAP_CAPTURE = (function () {
  "use strict";

  const DEFAULT_PROJECTION = "EPSG:3857";
  const FETCH_CONCURRENCY = 6;
  const MAX_GRID_ZOOM = 24;
  const BASEMAP_PREFIX = "Basemap: ";  // MapView's tethys_legend_title for basemap layers

  function getCurrentBasemap(map) {
    const layer = map.getLayers().getArray().find((l) =>
      typeof l.tethys_legend_title === "string" &&
      l.tethys_legend_title.startsWith(BASEMAP_PREFIX) &&
      l.getVisible()
    );
    return layer ? { layer, label: layer.tethys_legend_title.slice(BASEMAP_PREFIX.length) } : null;
  }

  function getTileLayers(basemap) {
    const layers = basemap.layer instanceof ol.layer.Group
      ? basemap.layer.getLayersArray()
      : [basemap.layer];
    return layers.filter((layer) => layer.getVisible() && layer instanceof ol.layer.Tile);
  }

  function getXyzTileGrid(source) {
    const mercator = ol.proj.get(DEFAULT_PROJECTION);
    const projection = source.getProjection() || mercator;
    const halfWorld = mercator.getExtent()[2];

    if (!ol.proj.equivalent(projection, mercator)) { return null; }

    const grid = source.getTileGridForProjection(projection);
    if (!grid || grid.getMinZoom() !== 0) { return null; }

    const maxZoom = Math.min(grid.getMaxZoom(), MAX_GRID_ZOOM);
    for (let z = 0; z <= maxZoom; z++) {
      const origin = grid.getOrigin(z);
      let tileSize = grid.getTileSize(z);
      tileSize = Array.isArray(tileSize) ? tileSize : [tileSize, tileSize];
      const expected = 2 * halfWorld / (tileSize[0] * Math.pow(2, z));

      if (tileSize[0] !== tileSize[1] ||
          Math.abs(origin[0] + halfWorld) > 1 || Math.abs(origin[1] - halfWorld) > 1 ||
          Math.abs(grid.getResolution(z) - expected) / expected > 1e-6) {
        return null;
      }
    }
    return grid;
  }

  // Work out which tiles to fetch. 
  // Returns {error} if the basemap or zoom range can't be captured
  function getPlan(basemap, extent, minZoom, maxZoom) {
    const layers = getTileLayers(basemap);
    // A single-layer basemap's opacity is already its layer's opacity; don't apply it twice
    const groupOpacity = basemap.layer instanceof ol.layer.Group ? basemap.layer.getOpacity() : 1;
    const plan = { sources: [], opacities: [], count: 0, zoomLimit: MAX_GRID_ZOOM };

    if (!layers.length) {
      return { error: "This basemap has no tile layers to download." };
    }

    for (const layer of layers) {
      const source = layer.getSource();
      const grid = source.getTileUrlFunction ? getXyzTileGrid(source) : null;
      if (!grid) {
        return { error: `The "${basemap.label}" basemap does not use the standard web map tile grid, ` +
                        "so it can't be saved as MBTiles." };
      }
      if (isBlockedSource(source)) {
        return { error: "OpenStreetMap's tile usage policy doesn't allow bulk downloads." };
      }
      if (source.getState() !== "ready") {
        return { error: "The basemap is still loading." };
      }

      let tileSize = grid.getTileSize(0);
      tileSize = Array.isArray(tileSize) ? tileSize : [tileSize, tileSize];
      if (plan.tileSize && plan.tileSize[0] !== tileSize[0]) {
        return { error: `The "${basemap.label}" basemap mixes tile sizes, so it can't be saved as MBTiles.` };
      }

      plan.tileSize = tileSize;
      plan.grid = grid;
      plan.zoomLimit = Math.min(plan.zoomLimit, grid.getMaxZoom());
      plan.sources.push(source);
      plan.opacities.push(layer.getOpacity() * groupOpacity);
    }

    if (!Number.isInteger(minZoom) || !Number.isInteger(maxZoom) || minZoom < 0 || minZoom > maxZoom) {
      return { error: "Enter a valid zoom range." };
    }
    if (maxZoom > plan.zoomLimit) {
      return { error: `The max zoom for this basemap is ${plan.zoomLimit}.` };
    }

    // Clip to the world so we don't count tiles that don't exist
    plan.extent = ol.extent.getIntersection(extent, ol.proj.get(DEFAULT_PROJECTION).getExtent());
    if (ol.extent.isEmpty(plan.extent)) {
      return { error: "The selected area is outside the map." };
    }

    plan.minZoom = minZoom;
    plan.maxZoom = maxZoom;
    for (let z = minZoom; z <= maxZoom; z++) {
      const range = plan.grid.getTileRangeForExtentAndZ(plan.extent, z);
      plan.count += range.getWidth() * range.getHeight();
    }
    return plan;
  }

  function fetchTile(url, attempts) {
    return fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (response.status === 204 || response.status === 404) { return null; }
        if (!response.ok) { throw new Error(`HTTP ${response.status}`); }
        return response.blob();
      })
      .catch((error) => {
        if (attempts > 1) { return fetchTile(url, attempts - 1); }
        throw error;
      })
      .then((blob) => (blob && blob.size ? blob : null));
  }

  // Draw one tile from each basemap layer into a single PNG.
  // A single-layer basemap keeps its original tile bytes (e.g. JPEG imagery).
  function compositeTiles(blobs, opacities, tileSize) {
    if (blobs.length === 1) { return Promise.resolve(blobs[0]); }
    if (!blobs.some(Boolean)) { return Promise.resolve(null); }

    return Promise.all(blobs.map((blob) => (blob ? createImageBitmap(blob) : null)))
      .then((images) => {
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");
        canvas.width = tileSize[0];
        canvas.height = tileSize[1];
        images.forEach((image, i) => {
          if (!image) { return; }
          ctx.globalAlpha = opacities[i];
          ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
          image.close();
        });
        return new Promise((resolve, reject) => {
          canvas.toBlob((blob) => {
            blob ? resolve(blob) : reject(new Error("A tile could not be combined."));
          }, "image/png");
        });
      });
  }

  function checkResponse(response) {
    if (!response.ok) {
      return response.text().then((text) => {
        let message = text;
        try { message = JSON.parse(text).error || text; } catch (e) { /* plain-text error */ }
        throw new Error(message || `The capture could not be saved (HTTP ${response.status}).`);
      });
    }
    return response.json();
  }

  /**
   * Fetch the visible basemap's tiles in the browser and upload them as a capture.
   * The server builds the MBTiles file inline, so this resolves with the capture's
   * final status (the upload endpoint's JSON response).
   */
  function capture({ map, extent, name, minZoom, maxZoom, uploadUrl, csrfToken, onProgress, onUploading }) {
    const basemap = getCurrentBasemap(map);
    if (!basemap) {
      return Promise.reject(new Error("Select a basemap to capture."));
    }
    const plan = getPlan(basemap, extent, minZoom, maxZoom);
    if (plan.error) {
      return Promise.reject(new Error(plan.error));
    }

    const projection = ol.proj.get(DEFAULT_PROJECTION);
    const coords = [];
    for (let z = plan.minZoom; z <= plan.maxZoom; z++) {
      const range = plan.grid.getTileRangeForExtentAndZ(plan.extent, z);
      for (let x = range.minX; x <= range.maxX; x++) {
        for (let y = range.minY; y <= range.maxY; y++) {
          coords.push([z, x, y]);
        }
      }
    }

    const results = new Array(coords.length);
    let next = 0;
    let done = 0;
    let failed = false;

    const runWorker = () => {
      if (failed || next >= coords.length) { return Promise.resolve(); }
      const index = next++;
      const coord = coords[index];

      return Promise.all(plan.sources.map((source) => {
        const url = source.getTileUrlFunction()(coord, 1, projection);
        return url ? fetchTile(url, 3) : null;
      }))
        .then((blobs) => compositeTiles(blobs, plan.opacities, plan.tileSize))
        .then((blob) => {
          results[index] = blob;
          done++;
          if (onProgress) { onProgress(done, coords.length); }
          return runWorker();
        });
    };

    const workers = [];
    for (let i = 0; i < Math.min(FETCH_CONCURRENCY, coords.length); i++) {
      workers.push(runWorker());
    }

    return Promise.all(workers)
      .catch((error) => {
        failed = true;
        // fetch rejects with a TypeError when the tile server doesn't send CORS headers
        if (error instanceof TypeError) {
          throw new Error(`The "${basemap.label}" server does not allow its tiles to be downloaded ` +
                          "(it does not send CORS headers).");
        }
        throw new Error(`A tile could not be downloaded (${error.message}).`);
      })
      .then(() => {
        const parts = [];
        const index = [];
        results.forEach((blob, i) => {
          if (!blob) { return; }
          parts.push(blob);
          index.push(coords[i].concat(blob.size));
        });
        if (!index.length) {
          throw new Error("The basemap has no tiles in the selected area.");
        }

        const form = new FormData();
        form.append("tiles", new Blob(parts), "tiles.bin");
        form.append("index", JSON.stringify(index));
        form.append("bbox", plan.extent.join(","));
        form.append("name", name);
        form.append("source", basemap.label);

        if (onUploading) { onUploading(index.length); }

        return fetch(uploadUrl, {
          method: "POST",
          credentials: "same-origin",
          headers: { "X-CSRFToken": csrfToken },
          body: form,
        });
      })
      .then(checkResponse);
  }
  // Ask the server to download the tiles on a Dask worker. Rejects with error.browserOnly
  // set when only the browser can download this basemap.
  function startServerCapture({ map, extent, name, minZoom, maxZoom, daskScheduler, maxRequestsPerSecond, serverUrl, csrfToken }) {
    const basemap = getCurrentBasemap(map);
    if (!basemap) {
      return Promise.reject(new Error("Select a basemap to capture."));
    }
    const plan = getPlan(basemap, extent, minZoom, maxZoom);
    if (plan.error) {
      return Promise.reject(new Error(plan.error));
    }

    return fetch(serverUrl, {
      method: "POST",
      credentials: "same-origin",
      headers: { "X-CSRFToken": csrfToken, "Content-Type": "application/json" },
      body: JSON.stringify({
        name,
        source: basemap.label,
        bbox: plan.extent,
        min_zoom: plan.minZoom,
        max_zoom: plan.maxZoom,
        tile_size: plan.tileSize[0],
        max_requests_per_second: maxRequestsPerSecond,
        dask_scheduler: daskScheduler,
      }),
    }).then((response) => {
      if (response.ok) { return response.json(); }
      return response.text().then((text) => {
        let data = {};
        try { data = JSON.parse(text); } catch (e) { /* plain-text error */ }
        const error = new Error(data.error || text || `HTTP ${response.status}`);
        error.browserOnly = !!data.browser_only;
        throw error;
      });
    });
  }

  // Poll the capture's status until it's ready or failed. onStatus(s) is called on each check
  // (server downloads include s.done and s.total).
  function waitForCapture(result, onStatus, interval = 2000) {
    if (result.status !== "processing") { return Promise.resolve(result); }

    const poll = () => new Promise((resolve) => setTimeout(resolve, interval))
      .then(() => fetch(result.status_url, { credentials: "same-origin" }))
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Could not check the capture status (HTTP ${response.status}).`);
        }
        return response.json();
      })
      .then((s) => {
        if (s.status === "ready") { return { ...result, ...s }; }
        if (s.status === "failed") { throw new Error(s.error || "The capture could not be built."); }
        if (s.status !== "processing") { return { ...result, ...s }; }  // e.g. cancelled
        if (onStatus) { onStatus(s); }
        return poll();
      });

    return poll();
  }

  // Rough tiles per second when nothing caps the rate. Rough guesses:
  const UNCAPPED_SERVER_RATE = 150;
  const BROWSER_RATE = 40;

  function formatDuration(seconds) {
    if (seconds < 90) { return `${Math.max(1, Math.round(seconds))} s`; }
    const minutes = Math.round(seconds / 60);
    if (minutes < 90) { return `${minutes} min`; }
    const h = Math.floor(minutes / 60);
    const m = minutes % 60;
    return m ? `${h} h ${m} min` : `${h} h`;
  }

  function describePlan(count, { onServer = false, rate = null } = {}) {
    const capped = onServer && rate > 0;
    const perSecond = capped ? rate : (onServer ? UNCAPPED_SERVER_RATE : BROWSER_RATE);
    const line = `${count.toLocaleString()} tiles · about ${formatDuration(count / perSecond)}`;
    return capped ? `${line} at ${rate}/s` : line;
  }


  function progressReporter() {
    let first = null;
    return (s) => {
      if (!s.total) { return "Processing on the server…"; }
      const now = Date.now();
      if (!first || s.done < first.done) { first = { done: s.done, at: now }; }
      const elapsed = (now - first.at) / 1000;
      const perSecond = elapsed > 0 ? (s.done - first.done) / elapsed : 0;
      const left = perSecond > 0
        ? ` · about ${formatDuration((s.total - s.done) / perSecond)} left`
        : "";
      const percent = Math.floor((100 * s.done) / s.total);
      return `Downloading on the server: ${s.done.toLocaleString()} / ${s.total.toLocaleString()} ` +
             `(${percent}%)${left}`;
    };
  }

  return {
    capture, startServerCapture, waitForCapture, getCurrentBasemap, getPlan,
    describePlan, formatDuration, progressReporter,
  };
})();
