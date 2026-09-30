(function () {
    'use strict';

    var rowLayers = new WeakMap();

        var MIN_SPAN = 1; // metres, EPSG:3857

    function cornersOf(extent) {
        return [
            [extent[0], extent[1]], // SW
            [extent[2], extent[1]], // SE
            [extent[2], extent[3]], // NE
            [extent[0], extent[3]], // NW
        ];
    }

    function resizeFromDrag(feature, pre) {
        if (!pre) return feature.getGeometry().getExtent();

        var old = cornersOf(pre);
        var ring = feature.getGeometry().getCoordinates()[0];
        var moved = null;
        var originIdx = -1;
        var bestDist = -1;

        ring.forEach(function (pt) {
            var nearest = 0;
            var nd = Infinity;
            old.forEach(function (c, i) {
                var d = Math.pow(pt[0] - c[0], 2) + Math.pow(pt[1] - c[1], 2);
                if (d < nd) { nd = d; nearest = i; }
            });
            if (nd > bestDist) { bestDist = nd; moved = pt; originIdx = nearest; }
        });

        if (bestDist <= 0 || originIdx < 0) return pre;

        var anchor = old[(originIdx + 2) % 4];
        var next = ol.extent.boundingExtent([moved, anchor]);

        if (next[2] - next[0] < MIN_SPAN || next[3] - next[1] < MIN_SPAN) return pre;
        return next;
    }

    function clearRow(row) {
        (rowLayers.get(row) || []).forEach(function (l) {
            window.basemapMap.removeLayer(l);
        });
        rowLayers.set(row, []);
    }

    function trackLayer(row, layer) {
        var layers = rowLayers.get(row) || [];
        layers.push(layer);
        rowLayers.set(row, layers);
        window.basemapMap.addLayer(layer);
    }

    function loadExisting(row) {
        var el = row.querySelector('script[id^="basemap-image-"]');
        if(!el) return null;

        var data = JSON.parse(el.textContent);
        if (!data.bounds || data.bounds.length !== 4) return null;
        
        var extent = data.bounds;
        if (data.epsg && data.epsg !== 3857) {
            extent = ol.proj.transformExtent(extent, 'EPSG:' + data.epsg, 'EPSG:3857');
        }

        addOverlay(row, data.url, extent, false);
        return extent;
    }
    
    function placeImage(row, file) {
        if (!window.basemapMap) return;

        var url = URL.createObjectURL(file);
        var probe = new Image();

        probe.onload = function () {
            var view = window.basemapMap.getView();
            var center = view.getCenter();
            var res = view.getResolution();
            var w = res * 400;
            var h = w * (probe.naturalHeight / probe.naturalWidth);
            var extent = [
                center[0] - w / 2,
                center[1] - h / 2,
                center[0] + w / 2,
                center[1] + h / 2,
            ];

            addOverlay(row, url, extent, true);
        };
        
        probe.src = url;
    }

    function addOverlay(row, url, extent, writeInput) {
        var layer = new ol.layer.Image({
            source: new ol.source.ImageStatic({
                url: url,
                imageExtent: extent,
                projection: 'EPSG:3857',
            }),
            opacity: 0.7,
        });

        var feature = new ol.Feature(ol.geom.Polygon.fromExtent(extent));
        var vectorSource = new ol.source.Vector({ features: [feature] });
        var vectorLayer = new ol.layer.Vector({
            source: vectorSource,
            style: new ol.style.Style({
                stroke: new ol.style.Stroke({ color: '#ff0', width: 2 }),
                fill: new ol.style.Fill({ color: 'rgba(255,255,0,0.05)' }),
            }),
        });

        trackLayer(row, layer);
        trackLayer(row, vectorLayer);

        var input = row.querySelector('input[name$="-georeference"]');

        function write(e) {
            if (input) input.value = JSON.stringify({ epsg: 3857, bounds: e});
        }
        if (writeInput) {
            write(extent);
        }

        var translate = new ol.interaction.Translate({ features: new ol.Collection([feature]) });
        var modify = new ol.interaction.Modify(
            { 
                source: vectorSource ,
                insertVertexCondition: ol.events.condition.never,
            }
        );

        var preExtent = null;

        function applyExtent(e) {
            feature.getGeometry().setCoordinates(
                ol.geom.Polygon.fromExtent(e).getCoordinates()
            );
            layer.setSource(new ol.source.ImageStatic({
                url: url, imageExtent: e, projection: 'EPSG:3857',
            }));
            write(e);
        }
        
        translate.on('translateend', function () {
            applyExtent(feature.getGeometry().getExtent());
        })

        modify.on('modifystart', function () {
            preExtent = feature.getGeometry().getExtent();
        });

        modify.on('modifyend', function () {
            applyExtent(resizeFromDrag(feature, preExtent));
        });

        window.basemapMap.addInteraction(translate);
        window.basemapMap.addInteraction(modify);
    }

    document.addEventListener('DOMContentLoaded', function () {
        var anchor = document.querySelector('.inline-group');
        if (!anchor) return;

        var container = document.createElement('div');
        container.id = 'basemap-service-map';
        container.style.cssText = 'width:100%;height:500px;border:1px solid #ccc;margin:20px 0;';
        anchor.parentNode.insertBefore(container, anchor);

        window.basemapMap = new ol.Map({
            target: container,
            layers: [new ol.layer.Tile({ source: new ol.source.OSM() })],
            view: new ol.View({
                center: ol.proj.fromLonLat([0, 20]),
                zoom: 2
            })
        });
        var union = ol.extent.createEmpty();
        document.querySelectorAll('.inline-related').forEach(function (row) {
            var extent = loadExisting(row);
            if (extent) {
                ol.extent.extend(union, extent);
            }
        });
        if (!ol.extent.isEmpty(union)) {
            window.basemapMap.getView().fit(union, { padding: [40, 40, 40, 40] });
        }
    });

    document.addEventListener('change', function (event) {
        if (event.target.type !== 'file') return;
        var file = event.target.files[0];
        if (!file) return;

        var row = event.target.closest('.inline-related');
        clearRow(row);
        placeImage(row, file);
    });
})();

