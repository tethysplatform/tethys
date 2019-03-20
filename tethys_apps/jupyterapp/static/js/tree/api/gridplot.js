"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var models_1 = require("./models");
function or_else(value, default_value) {
    if (value === undefined)
        return default_value;
    else
        return value;
}
function nope() {
    throw new Error("this shouldn't have happened");
}
function gridplot(children, opts) {
    if (opts === void 0) { opts = {}; }
    var toolbar_location = or_else(opts.toolbar_location, "above");
    var sizing_mode = or_else(opts.sizing_mode, "fixed");
    var merge_tools = or_else(opts.merge_tools, true);
    var tools = [];
    var rows = [];
    for (var _i = 0, children_1 = children; _i < children_1.length; _i++) {
        var row = children_1[_i];
        var row_tools = [];
        var row_children = [];
        for (var _a = 0, row_1 = row; _a < row_1.length; _a++) {
            var item = row_1[_a];
            if (item == null) {
                var width = 0;
                var height = 0;
                for (var _b = 0, row_2 = row; _b < row_2.length; _b++) {
                    var neighbor = row_2[_b];
                    if (neighbor instanceof models_1.Plot) {
                        width = neighbor.plot_width;
                        height = neighbor.plot_height;
                        break;
                    }
                }
                item = new models_1.Spacer({ width: width, height: height });
            }
            else if (item instanceof models_1.Plot) {
                row_tools.push.apply(row_tools, item.toolbar.tools);
                item.toolbar_location = null;
            }
            item.sizing_mode = sizing_mode;
            row_children.push(item);
        }
        tools.push.apply(tools, row_tools);
        rows.push(new models_1.Row({ children: row_children, sizing_mode: sizing_mode }));
    }
    var grid = new models_1.Column({ children: rows, sizing_mode: sizing_mode });
    if (!merge_tools || toolbar_location == null)
        return grid;
    var toolbar_sizing_mode;
    if (sizing_mode == "fixed") {
        if (toolbar_location == "above" || toolbar_location == "below")
            toolbar_sizing_mode = "scale_width";
        else
            toolbar_sizing_mode = "scale_height";
    }
    else
        toolbar_sizing_mode = sizing_mode;
    var toolbar = new models_1.ToolbarBox({
        toolbar: new models_1.ProxyToolbar({ tools: tools }),
        toolbar_location: toolbar_location,
        sizing_mode: toolbar_sizing_mode,
    });
    switch (toolbar_location) {
        case "above":
            return new models_1.Column({ children: [toolbar, grid], sizing_mode: sizing_mode });
        case "below":
            return new models_1.Column({ children: [grid, toolbar], sizing_mode: sizing_mode });
        case "left":
            return new models_1.Row({ children: [toolbar, grid], sizing_mode: sizing_mode });
        case "right":
            return new models_1.Row({ children: [grid, toolbar], sizing_mode: sizing_mode });
        default:
            return nope();
    }
}
exports.gridplot = gridplot;
