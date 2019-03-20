"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var document_1 = require("../document");
var dom_1 = require("../core/dom");
var base = require("../base");
var dom_2 = require("./dom");
function _create_view(model) {
    var view = new model.default_view({ model: model, parent: null });
    base.index[model.id] = view;
    return view;
}
function add_document_standalone(document, element, roots, use_for_title) {
    if (roots === void 0) { roots = {}; }
    if (use_for_title === void 0) { use_for_title = false; }
    // this is a LOCAL index of views used only by this particular rendering
    // call, so we can remove the views we create.
    var views = {};
    function render_model(model) {
        var root_el;
        if (model.id in roots)
            root_el = roots[model.id];
        else if (element.classList.contains(dom_2.BOKEH_ROOT))
            root_el = element;
        else {
            root_el = dom_1.div({ class: dom_2.BOKEH_ROOT });
            element.appendChild(root_el);
        }
        var view = _create_view(model);
        view.renderTo(root_el);
        views[model.id] = view;
    }
    function unrender_model(model) {
        var id = model.id;
        if (id in views) {
            var view = views[id];
            view.remove();
            delete views[id];
            delete base.index[id];
        }
    }
    for (var _i = 0, _a = document.roots(); _i < _a.length; _i++) {
        var model = _a[_i];
        render_model(model);
    }
    if (use_for_title)
        window.document.title = document.title();
    document.on_change(function (event) {
        if (event instanceof document_1.RootAddedEvent)
            render_model(event.model);
        else if (event instanceof document_1.RootRemovedEvent)
            unrender_model(event.model);
        else if (use_for_title && event instanceof document_1.TitleChangedEvent)
            window.document.title = event.title;
    });
    return views;
}
exports.add_document_standalone = add_document_standalone;
