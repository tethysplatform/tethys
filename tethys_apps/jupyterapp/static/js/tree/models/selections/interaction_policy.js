"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var model_1 = require("../../model");
var selection_1 = require("../selections/selection");
var SelectionPolicy = /** @class */ (function (_super) {
    tslib_1.__extends(SelectionPolicy, _super);
    function SelectionPolicy() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    SelectionPolicy.prototype.do_selection = function (hit_test_result, source, final, append) {
        if (hit_test_result === null) {
            return false;
        }
        else {
            source.selected.update(hit_test_result, final, append);
            //new selection created in order for python-side change detection machinery
            //to detect change in the source's selected property.
            var selected = new selection_1.Selection();
            selected.update(source.selected, final, false);
            source.selected = selected;
            source._select.emit();
            return !source.selected.is_empty();
        }
    };
    return SelectionPolicy;
}(model_1.Model));
exports.SelectionPolicy = SelectionPolicy;
SelectionPolicy.prototype.type = "SelectionPolicy";
var IntersectRenderers = /** @class */ (function (_super) {
    tslib_1.__extends(IntersectRenderers, _super);
    function IntersectRenderers() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    IntersectRenderers.prototype.hit_test = function (geometry, renderer_views) {
        var hit_test_result_renderers = [];
        for (var _i = 0, renderer_views_1 = renderer_views; _i < renderer_views_1.length; _i++) {
            var r = renderer_views_1[_i];
            var result = r.hit_test(geometry);
            if (result !== null)
                hit_test_result_renderers.push(result);
        }
        if (hit_test_result_renderers.length > 0) {
            var hit_test_result = hit_test_result_renderers[0];
            for (var _a = 0, hit_test_result_renderers_1 = hit_test_result_renderers; _a < hit_test_result_renderers_1.length; _a++) {
                var hit_test_result_other = hit_test_result_renderers_1[_a];
                hit_test_result.update_through_intersection(hit_test_result_other);
            }
            return hit_test_result;
        }
        else {
            return null;
        }
    };
    return IntersectRenderers;
}(SelectionPolicy));
exports.IntersectRenderers = IntersectRenderers;
IntersectRenderers.prototype.type = "IntersectRenderers";
var UnionRenderers = /** @class */ (function (_super) {
    tslib_1.__extends(UnionRenderers, _super);
    function UnionRenderers() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    UnionRenderers.prototype.hit_test = function (geometry, renderer_views) {
        var hit_test_result_renderers = [];
        for (var _i = 0, renderer_views_2 = renderer_views; _i < renderer_views_2.length; _i++) {
            var r = renderer_views_2[_i];
            var result = r.hit_test(geometry);
            if (result !== null)
                hit_test_result_renderers.push(result);
        }
        if (hit_test_result_renderers.length > 0) {
            var hit_test_result = hit_test_result_renderers[0];
            for (var _a = 0, hit_test_result_renderers_2 = hit_test_result_renderers; _a < hit_test_result_renderers_2.length; _a++) {
                var hit_test_result_other = hit_test_result_renderers_2[_a];
                hit_test_result.update_through_union(hit_test_result_other);
            }
            return hit_test_result;
        }
        else {
            return null;
        }
    };
    return UnionRenderers;
}(SelectionPolicy));
exports.UnionRenderers = UnionRenderers;
UnionRenderers.prototype.type = "UnionRenderers";
