"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var signaling_1 = require("core/signaling");
var projections_1 = require("core/util/projections");
var plot_canvas_1 = require("./plot_canvas");
var gmaps_ready = new signaling_1.Signal0({}, "gmaps_ready");
var load_google_api = function (api_key) {
    _bokeh_gmaps_callback = function () { return gmaps_ready.emit(); };
    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = "https://maps.googleapis.com/maps/api/js?key=" + api_key + "&callback=_bokeh_gmaps_callback";
    document.body.appendChild(script);
};
var GMapPlotCanvasView = /** @class */ (function (_super) {
    tslib_1.__extends(GMapPlotCanvasView, _super);
    function GMapPlotCanvasView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    GMapPlotCanvasView.prototype.initialize = function (options) {
        var _this = this;
        this.pause();
        _super.prototype.initialize.call(this, options);
        this._tiles_loaded = false;
        this.zoom_count = 0;
        var _a = this.model.plot.map_options, zoom = _a.zoom, lat = _a.lat, lng = _a.lng;
        this.initial_zoom = zoom;
        this.initial_lat = lat;
        this.initial_lng = lng;
        this.canvas_view.map_el.style.position = "absolute";
        if (typeof google === "undefined" || google.maps == null) {
            if (typeof _bokeh_gmaps_callback === "undefined") {
                load_google_api(this.model.plot.api_key);
            }
            gmaps_ready.connect(function () { return _this.request_render(); });
        }
        this.unpause();
    };
    GMapPlotCanvasView.prototype.update_range = function (range_info) {
        // RESET -------------------------
        if (range_info == null) {
            this.map.setCenter({ lat: this.initial_lat, lng: this.initial_lng });
            this.map.setOptions({ zoom: this.initial_zoom });
            _super.prototype.update_range.call(this, null);
            // PAN ----------------------------
        }
        else if (range_info.sdx != null || range_info.sdy != null) {
            this.map.panBy(range_info.sdx || 0, range_info.sdy || 0);
            _super.prototype.update_range.call(this, range_info);
            // ZOOM ---------------------------
        }
        else if (range_info.factor != null) {
            // The zoom count decreases the sensitivity of the zoom. (We could make this user configurable)
            var zoom_change = void 0;
            if (this.zoom_count !== 10) {
                this.zoom_count += 1;
                return;
            }
            this.zoom_count = 0;
            this.pause();
            _super.prototype.update_range.call(this, range_info);
            if (range_info.factor < 0)
                zoom_change = -1;
            else
                zoom_change = 1;
            var old_map_zoom = this.map.getZoom();
            var new_map_zoom = old_map_zoom + zoom_change;
            // Zooming out too far causes problems
            if (new_map_zoom >= 2) {
                this.map.setZoom(new_map_zoom);
                // Check we haven't gone out of bounds, and if we have undo the zoom
                var _a = this._get_projected_bounds(), proj_xstart = _a[0], proj_xend = _a[1];
                if (proj_xend - proj_xstart < 0) {
                    this.map.setZoom(old_map_zoom);
                }
            }
            this.unpause();
        }
        // Finally re-center
        this._set_bokeh_ranges();
    };
    GMapPlotCanvasView.prototype._build_map = function () {
        var _this = this;
        var maps = google.maps;
        this.map_types = {
            satellite: maps.MapTypeId.SATELLITE,
            terrain: maps.MapTypeId.TERRAIN,
            roadmap: maps.MapTypeId.ROADMAP,
            hybrid: maps.MapTypeId.HYBRID,
        };
        var mo = this.model.plot.map_options;
        var map_options = {
            center: new maps.LatLng(mo.lat, mo.lng),
            zoom: mo.zoom,
            disableDefaultUI: true,
            mapTypeId: this.map_types[mo.map_type],
            scaleControl: mo.scale_control,
            tilt: mo.tilt,
        };
        if (mo.styles != null)
            map_options.styles = JSON.parse(mo.styles);
        // create the map with above options in div
        this.map = new maps.Map(this.canvas_view.map_el, map_options);
        // update bokeh ranges whenever the map idles, which should be after most UI action
        maps.event.addListener(this.map, 'idle', function () { return _this._set_bokeh_ranges(); });
        // also need an event when bounds change so that map resizes trigger renders too
        maps.event.addListener(this.map, 'bounds_changed', function () { return _this._set_bokeh_ranges(); });
        maps.event.addListenerOnce(this.map, 'tilesloaded', function () { return _this._render_finished(); });
        // wire up listeners so that changes to properties are reflected
        this.connect(this.model.plot.properties.map_options.change, function () { return _this._update_options(); });
        this.connect(this.model.plot.map_options.properties.styles.change, function () { return _this._update_styles(); });
        this.connect(this.model.plot.map_options.properties.lat.change, function () { return _this._update_center('lat'); });
        this.connect(this.model.plot.map_options.properties.lng.change, function () { return _this._update_center('lng'); });
        this.connect(this.model.plot.map_options.properties.zoom.change, function () { return _this._update_zoom(); });
        this.connect(this.model.plot.map_options.properties.map_type.change, function () { return _this._update_map_type(); });
        this.connect(this.model.plot.map_options.properties.scale_control.change, function () { return _this._update_scale_control(); });
        this.connect(this.model.plot.map_options.properties.tilt.change, function () { return _this._update_tilt(); });
    };
    GMapPlotCanvasView.prototype._render_finished = function () {
        this._tiles_loaded = true;
        this.notify_finished();
    };
    GMapPlotCanvasView.prototype.has_finished = function () {
        return _super.prototype.has_finished.call(this) && this._tiles_loaded === true;
    };
    GMapPlotCanvasView.prototype._get_latlon_bounds = function () {
        var bounds = this.map.getBounds();
        var top_right = bounds.getNorthEast();
        var bottom_left = bounds.getSouthWest();
        var xstart = bottom_left.lng();
        var xend = top_right.lng();
        var ystart = bottom_left.lat();
        var yend = top_right.lat();
        return [xstart, xend, ystart, yend];
    };
    GMapPlotCanvasView.prototype._get_projected_bounds = function () {
        var _a = this._get_latlon_bounds(), xstart = _a[0], xend = _a[1], ystart = _a[2], yend = _a[3];
        var _b = projections_1.wgs84_mercator.forward([xstart, ystart]), proj_xstart = _b[0], proj_ystart = _b[1];
        var _c = projections_1.wgs84_mercator.forward([xend, yend]), proj_xend = _c[0], proj_yend = _c[1];
        return [proj_xstart, proj_xend, proj_ystart, proj_yend];
    };
    GMapPlotCanvasView.prototype._set_bokeh_ranges = function () {
        var _a = this._get_projected_bounds(), proj_xstart = _a[0], proj_xend = _a[1], proj_ystart = _a[2], proj_yend = _a[3];
        this.frame.x_range.setv({ start: proj_xstart, end: proj_xend });
        this.frame.y_range.setv({ start: proj_ystart, end: proj_yend });
    };
    GMapPlotCanvasView.prototype._update_center = function (fld) {
        var c = this.map.getCenter().toJSON();
        c[fld] = this.model.plot.map_options[fld];
        this.map.setCenter(c);
        this._set_bokeh_ranges();
    };
    GMapPlotCanvasView.prototype._update_map_type = function () {
        this.map.setOptions({ mapTypeId: this.map_types[this.model.plot.map_options.map_type] });
    };
    GMapPlotCanvasView.prototype._update_scale_control = function () {
        this.map.setOptions({ scaleControl: this.model.plot.map_options.scale_control });
    };
    GMapPlotCanvasView.prototype._update_tilt = function () {
        this.map.setOptions({ tilt: this.model.plot.map_options.tilt });
    };
    GMapPlotCanvasView.prototype._update_options = function () {
        this._update_styles();
        this._update_center('lat');
        this._update_center('lng');
        this._update_zoom();
        this._update_map_type();
    };
    GMapPlotCanvasView.prototype._update_styles = function () {
        this.map.setOptions({ styles: JSON.parse(this.model.plot.map_options.styles) });
    };
    GMapPlotCanvasView.prototype._update_zoom = function () {
        this.map.setOptions({ zoom: this.model.plot.map_options.zoom });
        this._set_bokeh_ranges();
    };
    // this method is expected and called by PlotCanvasView.render
    GMapPlotCanvasView.prototype._map_hook = function (_ctx, frame_box) {
        var left = frame_box[0], top = frame_box[1], width = frame_box[2], height = frame_box[3];
        this.canvas_view.map_el.style.top = top + "px";
        this.canvas_view.map_el.style.left = left + "px";
        this.canvas_view.map_el.style.width = width + "px";
        this.canvas_view.map_el.style.height = height + "px";
        if (this.map == null && typeof google !== "undefined" && google.maps != null)
            this._build_map();
    };
    // this overrides the standard _paint_empty to make the inner canvas transparent
    GMapPlotCanvasView.prototype._paint_empty = function (ctx, frame_box) {
        var ow = this.canvas._width.value;
        var oh = this.canvas._height.value;
        var left = frame_box[0], top = frame_box[1], iw = frame_box[2], ih = frame_box[3];
        ctx.clearRect(0, 0, ow, oh);
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(0, oh);
        ctx.lineTo(ow, oh);
        ctx.lineTo(ow, 0);
        ctx.lineTo(0, 0);
        ctx.moveTo(left, top);
        ctx.lineTo(left + iw, top);
        ctx.lineTo(left + iw, top + ih);
        ctx.lineTo(left, top + ih);
        ctx.lineTo(left, top);
        ctx.closePath();
        ctx.fillStyle = this.model.plot.border_fill_color;
        ctx.fill();
    };
    return GMapPlotCanvasView;
}(plot_canvas_1.PlotCanvasView));
exports.GMapPlotCanvasView = GMapPlotCanvasView;
var GMapPlotCanvas = /** @class */ (function (_super) {
    tslib_1.__extends(GMapPlotCanvas, _super);
    function GMapPlotCanvas(attrs) {
        return _super.call(this, attrs) || this;
    }
    GMapPlotCanvas.initClass = function () {
        this.prototype.type = 'GMapPlotCanvas';
        this.prototype.default_view = GMapPlotCanvasView;
    };
    GMapPlotCanvas.prototype.initialize = function () {
        this.use_map = true;
        _super.prototype.initialize.call(this);
    };
    return GMapPlotCanvas;
}(plot_canvas_1.PlotCanvas));
exports.GMapPlotCanvas = GMapPlotCanvas;
GMapPlotCanvas.initClass();
