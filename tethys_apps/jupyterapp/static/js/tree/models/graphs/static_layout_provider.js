"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var layout_provider_1 = require("./layout_provider");
var p = require("../../core/properties");
var StaticLayoutProvider = /** @class */ (function (_super) {
    tslib_1.__extends(StaticLayoutProvider, _super);
    function StaticLayoutProvider(attrs) {
        return _super.call(this, attrs) || this;
    }
    StaticLayoutProvider.initClass = function () {
        this.prototype.type = "StaticLayoutProvider";
        this.define({
            graph_layout: [p.Any, {}],
        });
    };
    StaticLayoutProvider.prototype.get_node_coordinates = function (node_source) {
        var xs = [];
        var ys = [];
        var index = node_source.data.index;
        for (var i = 0, end = index.length; i < end; i++) {
            var point = this.graph_layout[index[i]];
            var _a = point != null ? point : [NaN, NaN], x = _a[0], y = _a[1];
            xs.push(x);
            ys.push(y);
        }
        return [xs, ys];
    };
    StaticLayoutProvider.prototype.get_edge_coordinates = function (edge_source) {
        var _a, _b;
        var xs = [];
        var ys = [];
        var starts = edge_source.data.start;
        var ends = edge_source.data.end;
        var has_paths = (edge_source.data.xs != null) && (edge_source.data.ys != null);
        for (var i = 0, endi = starts.length; i < endi; i++) {
            var in_layout = (this.graph_layout[starts[i]] != null) && (this.graph_layout[ends[i]] != null);
            if (has_paths && in_layout) {
                xs.push(edge_source.data.xs[i]);
                ys.push(edge_source.data.ys[i]);
            }
            else {
                var end = void 0, start = void 0;
                if (in_layout)
                    _a = [this.graph_layout[starts[i]], this.graph_layout[ends[i]]], start = _a[0], end = _a[1];
                else
                    _b = [[NaN, NaN], [NaN, NaN]], start = _b[0], end = _b[1];
                xs.push([start[0], end[0]]);
                ys.push([start[1], end[1]]);
            }
        }
        return [xs, ys];
    };
    return StaticLayoutProvider;
}(layout_provider_1.LayoutProvider));
exports.StaticLayoutProvider = StaticLayoutProvider;
StaticLayoutProvider.initClass();
