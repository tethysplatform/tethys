"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var model_1 = require("../../model");
var p = require("core/properties");
var array_1 = require("core/util/array");
var object_1 = require("core/util/object");
var Selection = /** @class */ (function (_super) {
    tslib_1.__extends(Selection, _super);
    function Selection(attrs) {
        return _super.call(this, attrs) || this;
    }
    Selection.initClass = function () {
        this.prototype.type = "Selection";
        this.define({
            indices: [p.Array, []],
            line_indices: [p.Array, []],
            multiline_indices: [p.Any, {}],
        });
        this.internal({
            final: [p.Boolean],
            selected_glyphs: [p.Array, []],
            get_view: [p.Any],
            image_indices: [p.Array, []],
        });
    };
    Selection.prototype.initialize = function () {
        var _this = this;
        _super.prototype.initialize.call(this);
        this['0d'] = { glyph: null, indices: [], flag: false, get_view: function () { return null; } };
        this['2d'] = { indices: {} };
        this['1d'] = { indices: this.indices };
        this.get_view = function () { return null; };
        this.connect(this.properties.indices.change, function () {
            return _this['1d'].indices = _this.indices;
        });
        this.connect(this.properties.line_indices.change, function () {
            _this['0d'].indices = _this.line_indices;
            if (_this.line_indices.length == 0)
                _this['0d'].flag = false;
            else
                _this['0d'].flag = true;
        });
        this.connect(this.properties.selected_glyphs.change, function () {
            return _this['0d'].glyph = _this.selected_glyph;
        });
        this.connect(this.properties.get_view.change, function () {
            return _this['0d'].get_view = _this.get_view;
        });
        this.connect(this.properties.multiline_indices.change, function () {
            return _this['2d'].indices = _this.multiline_indices;
        });
    };
    Object.defineProperty(Selection.prototype, "selected_glyph", {
        get: function () {
            if (this.selected_glyphs.length > 0)
                return this.selected_glyphs[0];
            else
                return null;
        },
        enumerable: true,
        configurable: true
    });
    Selection.prototype.add_to_selected_glyphs = function (glyph) {
        this.selected_glyphs.push(glyph);
    };
    Selection.prototype.update = function (selection, final, append) {
        this.final = final;
        if (append)
            this.update_through_union(selection);
        else {
            this.indices = selection.indices;
            this.line_indices = selection.line_indices;
            this.selected_glyphs = selection.selected_glyphs;
            this.get_view = selection.get_view;
            this.multiline_indices = selection.multiline_indices;
            this.image_indices = selection.image_indices;
        }
    };
    Selection.prototype.clear = function () {
        this.final = true;
        this.indices = [];
        this.line_indices = [];
        this.multiline_indices = {};
        this.get_view = function () { return null; };
        this.selected_glyphs = [];
    };
    Selection.prototype.is_empty = function () {
        return this.indices.length == 0 && this.line_indices.length == 0 && this.image_indices.length == 0;
    };
    Selection.prototype.update_through_union = function (other) {
        this.indices = array_1.union(other.indices, this.indices);
        this.selected_glyphs = array_1.union(other.selected_glyphs, this.selected_glyphs);
        this.line_indices = array_1.union(other.line_indices, this.line_indices);
        if (!this.get_view())
            this.get_view = other.get_view;
        this.multiline_indices = object_1.merge(other.multiline_indices, this.multiline_indices);
    };
    Selection.prototype.update_through_intersection = function (other) {
        this.indices = array_1.intersection(other.indices, this.indices);
        // TODO: think through and fix any logic below
        this.selected_glyphs = array_1.union(other.selected_glyphs, this.selected_glyphs);
        this.line_indices = array_1.union(other.line_indices, this.line_indices);
        if (!this.get_view())
            this.get_view = other.get_view;
        this.multiline_indices = object_1.merge(other.multiline_indices, this.multiline_indices);
    };
    return Selection;
}(model_1.Model));
exports.Selection = Selection;
Selection.initClass();
