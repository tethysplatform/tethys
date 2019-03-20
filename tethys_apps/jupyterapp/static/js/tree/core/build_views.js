"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var array_1 = require("./util/array");
function build_views(view_storage, models, options, cls) {
    if (cls === void 0) { cls = function (model) { return model.default_view; }; }
    var to_remove = array_1.difference(Object.keys(view_storage), models.map(function (model) { return model.id; }));
    for (var _i = 0, to_remove_1 = to_remove; _i < to_remove_1.length; _i++) {
        var model_id = to_remove_1[_i];
        view_storage[model_id].remove();
        delete view_storage[model_id];
    }
    var created_views = [];
    var new_models = models.filter(function (model) { return view_storage[model.id] == null; });
    for (var _a = 0, new_models_1 = new_models; _a < new_models_1.length; _a++) {
        var model = new_models_1[_a];
        var view_cls = cls(model);
        var view_options = tslib_1.__assign({}, options, { model: model, connect_signals: false });
        var view = new view_cls(view_options);
        view_storage[model.id] = view;
        created_views.push(view);
    }
    for (var _b = 0, created_views_1 = created_views; _b < created_views_1.length; _b++) {
        var view = created_views_1[_b];
        view.connect_signals();
    }
    return created_views;
}
exports.build_views = build_views;
function remove_views(view_storage) {
    for (var id in view_storage) {
        view_storage[id].remove();
        delete view_storage[id];
    }
}
exports.remove_views = remove_views;
