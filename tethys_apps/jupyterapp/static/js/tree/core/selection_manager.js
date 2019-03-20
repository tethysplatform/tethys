"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var has_props_1 = require("./has_props");
var selection_1 = require("models/selections/selection");
var glyph_renderer_1 = require("models/renderers/glyph_renderer");
var graph_renderer_1 = require("models/renderers/graph_renderer");
var p = require("./properties");
var SelectionManager = /** @class */ (function (_super) {
    tslib_1.__extends(SelectionManager, _super);
    function SelectionManager() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    SelectionManager.initClass = function () {
        this.prototype.type = "SelectionManager";
        this.internal({
            source: [p.Any],
        });
    };
    SelectionManager.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        this.inspectors = {};
    };
    SelectionManager.prototype.select = function (renderer_views, geometry, final, append) {
        if (append === void 0) { append = false; }
        // divide renderers into glyph_renderers or graph_renderers
        var glyph_renderer_views = [];
        var graph_renderer_views = [];
        for (var _i = 0, renderer_views_1 = renderer_views; _i < renderer_views_1.length; _i++) {
            var r = renderer_views_1[_i];
            if (r instanceof glyph_renderer_1.GlyphRendererView)
                glyph_renderer_views.push(r);
            else if (r instanceof graph_renderer_1.GraphRendererView)
                graph_renderer_views.push(r);
        }
        var did_hit = false;
        // graph renderer case
        for (var _a = 0, graph_renderer_views_1 = graph_renderer_views; _a < graph_renderer_views_1.length; _a++) {
            var r = graph_renderer_views_1[_a];
            var hit_test_result = r.model.selection_policy.hit_test(geometry, r);
            did_hit = did_hit || r.model.selection_policy.do_selection(hit_test_result, r.model, final, append);
        }
        // glyph renderers
        if (glyph_renderer_views.length > 0) {
            var hit_test_result = this.source.selection_policy.hit_test(geometry, glyph_renderer_views);
            did_hit = did_hit || this.source.selection_policy.do_selection(hit_test_result, this.source, final, append);
        }
        return did_hit;
    };
    SelectionManager.prototype.inspect = function (renderer_view, geometry) {
        var did_hit = false;
        if (renderer_view instanceof glyph_renderer_1.GlyphRendererView) {
            var hit_test_result = renderer_view.hit_test(geometry);
            if (hit_test_result != null) {
                did_hit = !hit_test_result.is_empty();
                var inspection = this.get_or_create_inspector(renderer_view.model);
                inspection.update(hit_test_result, true, false);
                this.source.setv({ inspected: inspection }, { silent: true });
                this.source.inspect.emit([renderer_view, { geometry: geometry }]);
            }
        }
        else if (renderer_view instanceof graph_renderer_1.GraphRendererView) {
            var hit_test_result = renderer_view.model.inspection_policy.hit_test(geometry, renderer_view);
            did_hit = did_hit || renderer_view.model.inspection_policy.do_inspection(hit_test_result, geometry, renderer_view, false, false);
        }
        return did_hit;
    };
    SelectionManager.prototype.clear = function (rview) {
        this.source.selected.clear();
        if (rview != null)
            this.get_or_create_inspector(rview.model).clear();
    };
    SelectionManager.prototype.get_or_create_inspector = function (rmodel) {
        if (this.inspectors[rmodel.id] == null)
            this.inspectors[rmodel.id] = new selection_1.Selection();
        return this.inspectors[rmodel.id];
    };
    return SelectionManager;
}(has_props_1.HasProps));
exports.SelectionManager = SelectionManager;
SelectionManager.initClass();
