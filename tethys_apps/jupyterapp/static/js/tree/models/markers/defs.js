"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var marker_1 = require("./marker");
var SQ3 = Math.sqrt(3);
function _one_line(ctx, r) {
    ctx.moveTo(-r, 0);
    ctx.lineTo(r, 0);
}
function _one_x(ctx, r) {
    ctx.moveTo(-r, r);
    ctx.lineTo(r, -r);
    ctx.moveTo(-r, -r);
    ctx.lineTo(r, r);
}
function _one_cross(ctx, r) {
    ctx.moveTo(0, r);
    ctx.lineTo(0, -r);
    ctx.moveTo(-r, 0);
    ctx.lineTo(r, 0);
}
function _one_diamond(ctx, r) {
    ctx.moveTo(0, r);
    ctx.lineTo(r / 1.5, 0);
    ctx.lineTo(0, -r);
    ctx.lineTo(-r / 1.5, 0);
    ctx.closePath();
}
function _one_hex(ctx, r) {
    var r2 = r / 2;
    var h = SQ3 * r2;
    ctx.moveTo(r, 0);
    ctx.lineTo(r2, -h);
    ctx.lineTo(-r2, -h);
    ctx.lineTo(-r, 0);
    ctx.lineTo(-r2, h);
    ctx.lineTo(r2, h);
    ctx.closePath();
}
function _one_tri(ctx, r) {
    var h = r * SQ3;
    var a = h / 3;
    ctx.moveTo(-r, a);
    ctx.lineTo(r, a);
    ctx.lineTo(0, a - h);
    ctx.closePath();
}
function asterisk(ctx, i, r, line, _fill) {
    var r2 = r * 0.65;
    _one_cross(ctx, r);
    _one_x(ctx, r2);
    if (line.doit) {
        line.set_vectorize(ctx, i);
        ctx.stroke();
    }
}
function circle(ctx, i, r, line, fill) {
    ctx.arc(0, 0, r, 0, 2 * Math.PI, false);
    if (fill.doit) {
        fill.set_vectorize(ctx, i);
        ctx.fill();
    }
    if (line.doit) {
        line.set_vectorize(ctx, i);
        ctx.stroke();
    }
}
function circle_cross(ctx, i, r, line, fill) {
    ctx.arc(0, 0, r, 0, 2 * Math.PI, false);
    if (fill.doit) {
        fill.set_vectorize(ctx, i);
        ctx.fill();
    }
    if (line.doit) {
        line.set_vectorize(ctx, i);
        _one_cross(ctx, r);
        ctx.stroke();
    }
}
function circle_x(ctx, i, r, line, fill) {
    ctx.arc(0, 0, r, 0, 2 * Math.PI, false);
    if (fill.doit) {
        fill.set_vectorize(ctx, i);
        ctx.fill();
    }
    if (line.doit) {
        line.set_vectorize(ctx, i);
        _one_x(ctx, r);
        ctx.stroke();
    }
}
function cross(ctx, i, r, line, _fill) {
    _one_cross(ctx, r);
    if (line.doit) {
        line.set_vectorize(ctx, i);
        ctx.stroke();
    }
}
function diamond(ctx, i, r, line, fill) {
    _one_diamond(ctx, r);
    if (fill.doit) {
        fill.set_vectorize(ctx, i);
        ctx.fill();
    }
    if (line.doit) {
        line.set_vectorize(ctx, i);
        ctx.stroke();
    }
}
function diamond_cross(ctx, i, r, line, fill) {
    _one_diamond(ctx, r);
    if (fill.doit) {
        fill.set_vectorize(ctx, i);
        ctx.fill();
    }
    if (line.doit) {
        line.set_vectorize(ctx, i);
        _one_cross(ctx, r);
        ctx.stroke();
    }
}
function hex(ctx, i, r, line, fill) {
    _one_hex(ctx, r);
    if (fill.doit) {
        fill.set_vectorize(ctx, i);
        ctx.fill();
    }
    if (line.doit) {
        line.set_vectorize(ctx, i);
        ctx.stroke();
    }
}
function inverted_triangle(ctx, i, r, line, fill) {
    ctx.rotate(Math.PI);
    _one_tri(ctx, r);
    ctx.rotate(-Math.PI);
    if (fill.doit) {
        fill.set_vectorize(ctx, i);
        ctx.fill();
    }
    if (line.doit) {
        line.set_vectorize(ctx, i);
        ctx.stroke();
    }
}
function square(ctx, i, r, line, fill) {
    var size = 2 * r;
    ctx.rect(-r, -r, size, size);
    if (fill.doit) {
        fill.set_vectorize(ctx, i);
        ctx.fill();
    }
    if (line.doit) {
        line.set_vectorize(ctx, i);
        ctx.stroke();
    }
}
function square_cross(ctx, i, r, line, fill) {
    var size = 2 * r;
    ctx.rect(-r, -r, size, size);
    if (fill.doit) {
        fill.set_vectorize(ctx, i);
        ctx.fill();
    }
    if (line.doit) {
        line.set_vectorize(ctx, i);
        _one_cross(ctx, r);
        ctx.stroke();
    }
}
function square_x(ctx, i, r, line, fill) {
    var size = 2 * r;
    ctx.rect(-r, -r, size, size);
    if (fill.doit) {
        fill.set_vectorize(ctx, i);
        ctx.fill();
    }
    if (line.doit) {
        line.set_vectorize(ctx, i);
        _one_x(ctx, r);
        ctx.stroke();
    }
}
function triangle(ctx, i, r, line, fill) {
    _one_tri(ctx, r);
    if (fill.doit) {
        fill.set_vectorize(ctx, i);
        ctx.fill();
    }
    if (line.doit) {
        line.set_vectorize(ctx, i);
        ctx.stroke();
    }
}
function dash(ctx, i, r, line, _fill) {
    _one_line(ctx, r);
    if (line.doit) {
        line.set_vectorize(ctx, i);
        ctx.stroke();
    }
}
function x(ctx, i, r, line, _fill) {
    _one_x(ctx, r);
    if (line.doit) {
        line.set_vectorize(ctx, i);
        ctx.stroke();
    }
}
function _mk_model(type, f) {
    var view = /** @class */ (function (_super) {
        tslib_1.__extends(class_1, _super);
        function class_1() {
            return _super !== null && _super.apply(this, arguments) || this;
        }
        class_1.initClass = function () {
            this.prototype._render_one = f;
        };
        return class_1;
    }(marker_1.MarkerView));
    view.initClass();
    var model = /** @class */ (function (_super) {
        tslib_1.__extends(class_2, _super);
        function class_2() {
            return _super !== null && _super.apply(this, arguments) || this;
        }
        class_2.initClass = function () {
            this.prototype.default_view = view;
            this.prototype.type = type;
        };
        return class_2;
    }(marker_1.Marker));
    model.initClass();
    return model;
}
// markers are final, so no need to export views
exports.Asterisk = _mk_model('Asterisk', asterisk);
exports.CircleCross = _mk_model('CircleCross', circle_cross);
exports.CircleX = _mk_model('CircleX', circle_x);
exports.Cross = _mk_model('Cross', cross);
exports.Diamond = _mk_model('Diamond', diamond);
exports.DiamondCross = _mk_model('DiamondCross', diamond_cross);
exports.Hex = _mk_model('Hex', hex);
exports.InvertedTriangle = _mk_model('InvertedTriangle', inverted_triangle);
exports.Square = _mk_model('Square', square);
exports.SquareCross = _mk_model('SquareCross', square_cross);
exports.SquareX = _mk_model('SquareX', square_x);
exports.Triangle = _mk_model('Triangle', triangle);
exports.Dash = _mk_model('Dash', dash);
exports.X = _mk_model('X', x);
exports.marker_funcs = {
    asterisk: asterisk,
    circle: circle,
    circle_cross: circle_cross,
    circle_x: circle_x,
    cross: cross,
    diamond: diamond,
    diamond_cross: diamond_cross,
    hex: hex,
    inverted_triangle: inverted_triangle,
    square: square,
    square_cross: square_cross,
    square_x: square_x,
    triangle: triangle,
    dash: dash,
    x: x,
};
