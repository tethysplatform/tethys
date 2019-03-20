"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var solver_1 = require("./solver");
var array_1 = require("../util/array");
function vstack(container, children) {
    var constraints = [];
    if (children.length > 0) {
        constraints.push(solver_1.EQ(array_1.head(children)._bottom, [-1, container._bottom]));
        constraints.push(solver_1.EQ(array_1.tail(children)._top, [-1, container._top]));
        constraints.push.apply(constraints, array_1.pairwise(children, function (prev, next) { return solver_1.EQ(prev._top, [-1, next._bottom]); }));
        for (var _i = 0, children_1 = children; _i < children_1.length; _i++) {
            var child = children_1[_i];
            constraints.push(solver_1.EQ(child._left, [-1, container._left]));
            constraints.push(solver_1.EQ(child._right, [-1, container._right]));
        }
    }
    return constraints;
}
exports.vstack = vstack;
function hstack(container, children) {
    var constraints = [];
    if (children.length > 0) {
        constraints.push(solver_1.EQ(array_1.head(children)._right, [-1, container._right]));
        constraints.push(solver_1.EQ(array_1.tail(children)._left, [-1, container._left]));
        constraints.push.apply(constraints, array_1.pairwise(children, function (prev, next) { return solver_1.EQ(prev._left, [-1, next._right]); }));
        for (var _i = 0, children_2 = children; _i < children_2.length; _i++) {
            var child = children_2[_i];
            constraints.push(solver_1.EQ(child._top, [-1, container._top]));
            constraints.push(solver_1.EQ(child._bottom, [-1, container._bottom]));
        }
    }
    return constraints;
}
exports.hstack = hstack;
