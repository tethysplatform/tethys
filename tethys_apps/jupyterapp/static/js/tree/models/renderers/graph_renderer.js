"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var renderer_1 = require("./renderer");
var graph_hit_test_policy_1 = require("../graphs/graph_hit_test_policy");
var p = require("core/properties");
var build_views_1 = require("core/build_views");
var GraphRendererView = /** @class */ (function (_super) {
    tslib_1.__extends(GraphRendererView, _super);
    function GraphRendererView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    GraphRendererView.prototype.initialize = function (options) {
        var _a;
        _super.prototype.initialize.call(this, options);
        this.xscale = this.plot_view.frame.xscales["default"];
        this.yscale = this.plot_view.frame.yscales["default"];
        this._renderer_views = {};
        _a = build_views_1.build_views(this._renderer_views, [this.model.node_renderer, this.model.edge_renderer], this.plot_view.view_options()), this.node_view = _a[0], this.edge_view = _a[1];
        this.set_data();
    };
    GraphRendererView.prototype.connect_signals = function () {
        var _this = this;
        _super.prototype.connect_signals.call(this);
        this.connect(this.model.layout_provider.change, function () { return _this.set_data(); });
        this.connect(this.model.node_renderer.data_source._select, function () { return _this.set_data(); });
        this.connect(this.model.node_renderer.data_source.inspect, function () { return _this.set_data(); });
        this.connect(this.model.node_renderer.data_source.change, function () { return _this.set_data(); });
        this.connect(this.model.edge_renderer.data_source._select, function () { return _this.set_data(); });
        this.connect(this.model.edge_renderer.data_source.inspect, function () { return _this.set_data(); });
        this.connect(this.model.edge_renderer.data_source.change, function () { return _this.set_data(); });
        var _a = this.plot_model.frame, x_ranges = _a.x_ranges, y_ranges = _a.y_ranges;
        for (var name_1 in x_ranges) {
            var rng = x_ranges[name_1];
            this.connect(rng.change, function () { return _this.set_data(); });
        }
        for (var name_2 in y_ranges) {
            var rng = y_ranges[name_2];
            this.connect(rng.change, function () { return _this.set_data(); });
        }
    };
    GraphRendererView.prototype.set_data = function (request_render) {
        if (request_render === void 0) { request_render = true; }
        var _a, _b;
        // TODO (bev) this is a bit clunky, need to make sure glyphs use the correct ranges when they call
        // mapping functions on the base Renderer class
        this.node_view.glyph.model.setv({ x_range_name: this.model.x_range_name, y_range_name: this.model.y_range_name }, { silent: true });
        this.edge_view.glyph.model.setv({ x_range_name: this.model.x_range_name, y_range_name: this.model.y_range_name }, { silent: true });
        // XXX
        var node_glyph = this.node_view.glyph;
        _a = this.model.layout_provider.get_node_coordinates(this.model.node_renderer.data_source), node_glyph._x = _a[0], node_glyph._y = _a[1];
        var edge_glyph = this.edge_view.glyph;
        _b = this.model.layout_provider.get_edge_coordinates(this.model.edge_renderer.data_source), edge_glyph._xs = _b[0], edge_glyph._ys = _b[1];
        node_glyph.index_data();
        edge_glyph.index_data();
        if (request_render)
            this.request_render();
    };
    GraphRendererView.prototype.render = function () {
        this.edge_view.render();
        this.node_view.render();
    };
    return GraphRendererView;
}(renderer_1.RendererView));
exports.GraphRendererView = GraphRendererView;
var GraphRenderer = /** @class */ (function (_super) {
    tslib_1.__extends(GraphRenderer, _super);
    function GraphRenderer(attrs) {
        return _super.call(this, attrs) || this;
    }
    GraphRenderer.initClass = function () {
        this.prototype.type = 'GraphRenderer';
        this.prototype.default_view = GraphRendererView;
        this.define({
            x_range_name: [p.String, 'default'],
            y_range_name: [p.String, 'default'],
            layout_provider: [p.Instance],
            node_renderer: [p.Instance],
            edge_renderer: [p.Instance],
            selection_policy: [p.Instance, function () { return new graph_hit_test_policy_1.NodesOnly(); }],
            inspection_policy: [p.Instance, function () { return new graph_hit_test_policy_1.NodesOnly(); }],
        });
        this.override({
            level: 'glyph',
        });
    };
    GraphRenderer.prototype.get_selection_manager = function () {
        return this.node_renderer.data_source.selection_manager;
    };
    return GraphRenderer;
}(renderer_1.Renderer));
exports.GraphRenderer = GraphRenderer;
GraphRenderer.initClass();
