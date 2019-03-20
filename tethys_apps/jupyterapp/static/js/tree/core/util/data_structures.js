"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var array_1 = require("./array");
var eq_1 = require("./eq");
var types_1 = require("./types");
var MultiDict = /** @class */ (function () {
    function MultiDict() {
        this._dict = {};
    }
    MultiDict.prototype._existing = function (key) {
        if (key in this._dict)
            return this._dict[key];
        else
            return null;
    };
    MultiDict.prototype.add_value = function (key, value) {
        /*
        if value == null
          throw new Error("Can't put null in this dict")
        if isArray(value)
          throw new Error("Can't put arrays in this dict")
        */
        var existing = this._existing(key);
        if (existing == null) {
            this._dict[key] = value;
        }
        else if (types_1.isArray(existing)) {
            existing.push(value);
        }
        else {
            this._dict[key] = [existing, value];
        }
    };
    MultiDict.prototype.remove_value = function (key, value) {
        var existing = this._existing(key);
        if (types_1.isArray(existing)) {
            var new_array = array_1.difference(existing, [value]);
            if (new_array.length > 0)
                this._dict[key] = new_array;
            else
                delete this._dict[key];
        }
        else if (eq_1.isEqual(existing, value)) {
            delete this._dict[key];
        }
    };
    MultiDict.prototype.get_one = function (key, duplicate_error) {
        var existing = this._existing(key);
        if (types_1.isArray(existing)) {
            if (existing.length === 1)
                return existing[0];
            else
                throw new Error(duplicate_error);
        }
        else
            return existing;
    };
    return MultiDict;
}());
exports.MultiDict = MultiDict;
var Set = /** @class */ (function () {
    function Set(obj) {
        if (obj == null)
            this._values = [];
        else if (obj instanceof Set)
            this._values = array_1.copy(obj._values);
        else {
            this._values = [];
            for (var _i = 0, obj_1 = obj; _i < obj_1.length; _i++) {
                var item = obj_1[_i];
                this.add(item);
            }
        }
    }
    Object.defineProperty(Set.prototype, "values", {
        get: function () {
            return array_1.copy(this._values).sort();
        },
        enumerable: true,
        configurable: true
    });
    Set.prototype.toString = function () {
        return "Set([" + this.values.join(",") + "])";
    };
    Object.defineProperty(Set.prototype, "size", {
        get: function () {
            return this._values.length;
        },
        enumerable: true,
        configurable: true
    });
    Set.prototype.has = function (item) {
        return this._values.indexOf(item) !== -1;
    };
    Set.prototype.add = function (item) {
        if (!this.has(item))
            this._values.push(item);
    };
    Set.prototype.remove = function (item) {
        var i = this._values.indexOf(item);
        if (i !== -1)
            this._values.splice(i, 1);
    };
    Set.prototype.toggle = function (item) {
        var i = this._values.indexOf(item);
        if (i === -1)
            this._values.push(item);
        else
            this._values.splice(i, 1);
    };
    Set.prototype.clear = function () {
        this._values = [];
    };
    Set.prototype.union = function (input) {
        input = new Set(input);
        return new Set(this._values.concat(input._values));
    };
    Set.prototype.intersect = function (input) {
        input = new Set(input);
        var output = new Set();
        for (var _i = 0, _a = input._values; _i < _a.length; _i++) {
            var item = _a[_i];
            if (this.has(item) && input.has(item))
                output.add(item);
        }
        return output;
    };
    Set.prototype.diff = function (input) {
        input = new Set(input);
        var output = new Set();
        for (var _i = 0, _a = this._values; _i < _a.length; _i++) {
            var item = _a[_i];
            if (!input.has(item))
                output.add(item);
        }
        return output;
    };
    Set.prototype.forEach = function (fn, thisArg) {
        for (var _i = 0, _a = this._values; _i < _a.length; _i++) {
            var value = _a[_i];
            fn.call(thisArg || this, value, value, this);
        }
    };
    return Set;
}());
exports.Set = Set;
