"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var models = require("./models/index");
var object_1 = require("./core/util/object");
exports.overrides = {};
var _all_models = object_1.clone(models);
exports.Models = (function (name) {
    var model = exports.overrides[name] || _all_models[name];
    if (model == null) {
        throw new Error("Model '" + name + "' does not exist. This could be due to a widget\n                     or a custom model not being registered before first usage.");
    }
    return model;
});
exports.Models.register = function (name, model) {
    exports.overrides[name] = model;
};
exports.Models.unregister = function (name) {
    delete exports.overrides[name];
};
exports.Models.register_models = function (models, force, errorFn) {
    if (force === void 0) { force = false; }
    if (models == null)
        return;
    for (var name_1 in models) {
        var model = models[name_1];
        if (force || !_all_models.hasOwnProperty(name_1))
            _all_models[name_1] = model;
        else if (errorFn != null)
            errorFn(name_1);
        else
            console.warn("Model '" + name_1 + "' was already registered");
    }
};
exports.register_models = exports.Models.register_models;
exports.Models.registered_names = function () { return Object.keys(_all_models); };
// "index" is a map from the toplevel model IDs rendered by
// embed.ts, to the view objects for those models. It doesn't
// contain all views, only those explicitly rendered to an element
// by embed.ts.
exports.index = {};
