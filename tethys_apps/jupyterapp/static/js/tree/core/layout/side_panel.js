"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var solver_1 = require("./solver");
var layout_canvas_1 = require("./layout_canvas");
var p = require("../properties");
var logging_1 = require("../logging");
var types_1 = require("../util/types");
// This table lays out the rules for configuring the baseline, alignment, etc. of
// title text, based on it's location and orientation
//
// side    orient        baseline   align     angle   normal-dist
// ------------------------------------------------------------------------------
// above   parallel      bottom     center    0       height
//         normal        middle     left      -90     width
//         horizontal    bottom     center    0       height
//         [angle > 0]   middle     left              width * sin + height * cos
//         [angle < 0]   middle     right             width * sin + height * cos
//
// below   parallel      top        center    0       height
//         normal        middle     right     90      width
//         horizontal    top        center    0       height
//         [angle > 0]   middle     right             width * sin + height * cos
//         [angle < 0]   middle     left              width * sin + height * cos
//
// left    parallel      bottom     center    90      height
//         normal        middle     right     0       width
//         horizontal    middle     right     0       width
//         [angle > 0]   middle     right             width * cos + height * sin
//         [angle < 0]   middle     right             width * cos + height + sin
//
// right   parallel      bottom     center   -90      height
//         normal        middle     left     0        width
//         horizontal    middle     left     0        width
//         [angle > 0]   middle     left              width * cos + height * sin
//         [angle < 0]   middle     left              width * cos + height + sin
var pi2 = Math.PI / 2;
var ALPHABETIC = 'alphabetic';
var TOP = 'top';
var BOTTOM = 'bottom';
var MIDDLE = 'middle';
var HANGING = 'hanging';
var LEFT = 'left';
var RIGHT = 'right';
var CENTER = 'center';
var _angle_lookup = {
    above: {
        parallel: 0,
        normal: -pi2,
        horizontal: 0,
        vertical: -pi2,
    },
    below: {
        parallel: 0,
        normal: pi2,
        horizontal: 0,
        vertical: pi2,
    },
    left: {
        parallel: -pi2,
        normal: 0,
        horizontal: 0,
        vertical: -pi2,
    },
    right: {
        parallel: pi2,
        normal: 0,
        horizontal: 0,
        vertical: pi2,
    },
};
var _baseline_lookup = {
    above: {
        justified: TOP,
        parallel: ALPHABETIC,
        normal: MIDDLE,
        horizontal: ALPHABETIC,
        vertical: MIDDLE,
    },
    below: {
        justified: BOTTOM,
        parallel: HANGING,
        normal: MIDDLE,
        horizontal: HANGING,
        vertical: MIDDLE,
    },
    left: {
        justified: TOP,
        parallel: ALPHABETIC,
        normal: MIDDLE,
        horizontal: MIDDLE,
        vertical: ALPHABETIC,
    },
    right: {
        justified: TOP,
        parallel: ALPHABETIC,
        normal: MIDDLE,
        horizontal: MIDDLE,
        vertical: ALPHABETIC,
    },
};
var _align_lookup = {
    above: {
        justified: CENTER,
        parallel: CENTER,
        normal: LEFT,
        horizontal: CENTER,
        vertical: LEFT,
    },
    below: {
        justified: CENTER,
        parallel: CENTER,
        normal: LEFT,
        horizontal: CENTER,
        vertical: LEFT,
    },
    left: {
        justified: CENTER,
        parallel: CENTER,
        normal: RIGHT,
        horizontal: RIGHT,
        vertical: CENTER,
    },
    right: {
        justified: CENTER,
        parallel: CENTER,
        normal: LEFT,
        horizontal: LEFT,
        vertical: CENTER,
    },
};
var _align_lookup_negative = {
    above: RIGHT,
    below: LEFT,
    left: RIGHT,
    right: LEFT,
};
var _align_lookup_positive = {
    above: LEFT,
    below: RIGHT,
    left: RIGHT,
    right: LEFT,
};
function isSizeable(model) {
    return "panel" in model;
}
exports.isSizeable = isSizeable;
function isSizeableView(view) {
    return isSizeable(view.model) && "get_size" in view;
}
exports.isSizeableView = isSizeableView;
exports._view_sizes = new WeakMap();
exports._view_constraints = new WeakMap();
function update_panel_constraints(view) {
    var s = view.solver;
    var size = view.get_size();
    var constraint = exports._view_constraints.get(view);
    if (constraint != null && s.has_constraint(constraint)) {
        if (exports._view_sizes.get(view) === size)
            return;
        s.remove_constraint(constraint);
    }
    constraint = solver_1.GE(view.model.panel._size, -size);
    s.add_constraint(constraint);
    exports._view_sizes.set(view, size);
    exports._view_constraints.set(view, constraint);
}
exports.update_panel_constraints = update_panel_constraints;
var SidePanel = /** @class */ (function (_super) {
    tslib_1.__extends(SidePanel, _super);
    function SidePanel(attrs) {
        return _super.call(this, attrs) || this;
    }
    SidePanel.initClass = function () {
        this.prototype.type = "SidePanel";
        this.internal({
            side: [p.String],
        });
    };
    SidePanel.prototype.toString = function () {
        return this.type + "(" + this.id + ", " + this.side + ")";
    };
    SidePanel.prototype.initialize = function () {
        _super.prototype.initialize.call(this);
        switch (this.side) {
            case "above":
                this._dim = 0;
                this._normals = [0, -1];
                this._size = this._height;
                break;
            case "below":
                this._dim = 0;
                this._normals = [0, 1];
                this._size = this._height;
                break;
            case "left":
                this._dim = 1;
                this._normals = [-1, 0];
                this._size = this._width;
                break;
            case "right":
                this._dim = 1;
                this._normals = [1, 0];
                this._size = this._width;
                break;
            default:
                logging_1.logger.error("unrecognized side: '" + this.side + "'");
        }
    };
    Object.defineProperty(SidePanel.prototype, "dimension", {
        get: function () {
            return this._dim;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(SidePanel.prototype, "normals", {
        get: function () {
            return this._normals;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(SidePanel.prototype, "is_horizontal", {
        get: function () {
            return this.side == "above" || this.side == "below";
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(SidePanel.prototype, "is_vertical", {
        get: function () {
            return this.side == "left" || this.side == "right";
        },
        enumerable: true,
        configurable: true
    });
    SidePanel.prototype.apply_label_text_heuristics = function (ctx, orient) {
        var side = this.side;
        var baseline;
        var align;
        if (types_1.isString(orient)) {
            baseline = _baseline_lookup[side][orient];
            align = _align_lookup[side][orient];
        }
        else {
            if (orient === 0) {
                baseline = "whatever"; // XXX: _baseline_lookup[side][orient]
                align = "whatever"; // XXX: _align_lookup[side][orient]
            }
            else if (orient < 0) {
                baseline = 'middle';
                align = _align_lookup_negative[side];
            }
            else {
                baseline = 'middle';
                align = _align_lookup_positive[side];
            }
        }
        ctx.textBaseline = baseline;
        ctx.textAlign = align;
    };
    SidePanel.prototype.get_label_angle_heuristic = function (orient) {
        return _angle_lookup[this.side][orient];
    };
    return SidePanel;
}(layout_canvas_1.LayoutCanvas));
exports.SidePanel = SidePanel;
SidePanel.initClass();
