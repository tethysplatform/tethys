"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var side_panel_1 = require("core/layout/side_panel");
var p = require("core/properties");
var proj = require("core/util/projections");
var object_1 = require("core/util/object");
var renderer_1 = require("../renderers/renderer");
var AnnotationView = /** @class */ (function (_super) {
    tslib_1.__extends(AnnotationView, _super);
    function AnnotationView() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    AnnotationView.prototype._get_size = function () {
        throw new Error("not implemented");
    };
    AnnotationView.prototype.get_size = function () {
        return this.model.visible ? Math.round(this._get_size()) : 0;
    };
    AnnotationView.prototype.set_data = function (source) {
        var _a, _b;
        var data = this.model.materialize_dataspecs(source);
        object_1.extend(this, data);
        if (this.plot_model.use_map) {
            var self_1 = this;
            if (self_1._x != null)
                _a = proj.project_xy(self_1._x, self_1._y), self_1._x = _a[0], self_1._y = _a[1];
            if (self_1._xs != null)
                _b = proj.project_xsys(self_1._xs, self_1._ys), self_1._xs = _b[0], self_1._ys = _b[1];
        }
    };
    return AnnotationView;
}(renderer_1.RendererView));
exports.AnnotationView = AnnotationView;
var Annotation = /** @class */ (function (_super) {
    tslib_1.__extends(Annotation, _super);
    function Annotation(attrs) {
        return _super.call(this, attrs) || this;
    }
    Annotation.initClass = function () {
        this.prototype.type = 'Annotation';
        this.define({
            plot: [p.Instance],
        });
        this.override({
            level: 'annotation',
        });
    };
    Annotation.prototype.add_panel = function (side) {
        if (this.panel == null || side !== this.panel.side) {
            var panel = new side_panel_1.SidePanel({ side: side });
            panel.attach_document(this.document);
            this.set_panel(panel);
        }
    };
    Annotation.prototype.set_panel = function (panel) {
        this.panel = panel;
        // If the annotation is in a side panel, we need to set level to overlay, so it is visible.
        this.level = 'overlay';
    };
    return Annotation;
}(renderer_1.Renderer));
exports.Annotation = Annotation;
Annotation.initClass();
