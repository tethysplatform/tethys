"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var kiwi_1 = require("kiwi");
exports.Variable = kiwi_1.Variable;
exports.Expression = kiwi_1.Expression;
exports.Constraint = kiwi_1.Constraint;
exports.Operator = kiwi_1.Operator;
exports.Strength = kiwi_1.Strength;
function _constrainer(op) {
    return function () {
        var terms = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            terms[_i] = arguments[_i];
        }
        return new kiwi_1.Constraint(new (kiwi_1.Expression.bind.apply(kiwi_1.Expression, [void 0].concat(terms)))(), op);
    };
}
function _weak_constrainer(op) {
    return function () {
        var terms = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            terms[_i] = arguments[_i];
        }
        return new kiwi_1.Constraint(new (kiwi_1.Expression.bind.apply(kiwi_1.Expression, [void 0].concat(terms)))(), op, kiwi_1.Strength.weak);
    };
}
exports.EQ = _constrainer(kiwi_1.Operator.Eq);
exports.LE = _constrainer(kiwi_1.Operator.Le);
exports.GE = _constrainer(kiwi_1.Operator.Ge);
exports.WEAK_EQ = _weak_constrainer(kiwi_1.Operator.Eq);
exports.WEAK_LE = _weak_constrainer(kiwi_1.Operator.Le);
exports.WEAK_GE = _weak_constrainer(kiwi_1.Operator.Ge);
var Solver = /** @class */ (function () {
    function Solver() {
        this.solver = new kiwi_1.Solver();
    }
    Solver.prototype.clear = function () {
        this.solver = new kiwi_1.Solver();
    };
    Solver.prototype.toString = function () {
        return "Solver(num_constraints=" + this.num_constraints + ", num_editables=" + this.num_editables + ")";
    };
    Object.defineProperty(Solver.prototype, "num_constraints", {
        get: function () {
            return this.solver.numConstraints;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Solver.prototype, "num_editables", {
        get: function () {
            return this.solver.numEditVariables;
        },
        enumerable: true,
        configurable: true
    });
    Solver.prototype.get_constraints = function () {
        return this.solver.getConstraints();
    };
    Solver.prototype.update_variables = function () {
        this.solver.updateVariables();
    };
    Solver.prototype.has_constraint = function (constraint) {
        return this.solver.hasConstraint(constraint);
    };
    Solver.prototype.add_constraint = function (constraint) {
        try {
            this.solver.addConstraint(constraint);
        }
        catch (e) {
            throw new Error(e.message + ": " + constraint.toString());
        }
    };
    Solver.prototype.remove_constraint = function (constraint) {
        this.solver.removeConstraint(constraint);
    };
    Solver.prototype.add_edit_variable = function (variable, strength) {
        this.solver.addEditVariable(variable, strength);
    };
    Solver.prototype.remove_edit_variable = function (variable) {
        this.solver.removeEditVariable(variable);
    };
    Solver.prototype.suggest_value = function (variable, value) {
        this.solver.suggestValue(variable, value);
    };
    return Solver;
}());
exports.Solver = Solver;
