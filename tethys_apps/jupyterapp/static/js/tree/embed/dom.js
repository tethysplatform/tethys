"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var dom_1 = require("../core/dom");
// Matches Bokeh CSS class selector. Setting all Bokeh parent element class names
// with this var prevents user configurations where css styling is unset.
exports.BOKEH_ROOT = "bk-root";
function inject_css(url) {
    var element = dom_1.link({ href: url, rel: "stylesheet", type: "text/css" });
    document.body.appendChild(element);
}
exports.inject_css = inject_css;
function inject_raw_css(css) {
    var element = dom_1.style({}, css);
    document.body.appendChild(element);
}
exports.inject_raw_css = inject_raw_css;
function _get_element(elementid) {
    var element = document.getElementById(elementid);
    if (element == null)
        throw new Error("Error rendering Bokeh model: could not find #" + elementid + " HTML tag");
    if (!document.body.contains(element))
        throw new Error("Error rendering Bokeh model: element #" + elementid + " must be under <body>");
    // If autoload script, replace script tag with div for embedding.
    if (element.tagName == "SCRIPT") {
        var root_el = dom_1.div({ class: exports.BOKEH_ROOT });
        dom_1.replaceWith(element, root_el);
        element = root_el;
    }
    return element;
}
function _resolve_element(item) {
    var elementid = item.elementid;
    if (elementid != null)
        return _get_element(elementid);
    else
        return document.body;
}
exports._resolve_element = _resolve_element;
function _resolve_root_elements(item) {
    var roots = {};
    if (item.roots != null) {
        for (var root_id in item.roots)
            roots[root_id] = _get_element(item.roots[root_id]);
    }
    return roots;
}
exports._resolve_root_elements = _resolve_root_elements;
