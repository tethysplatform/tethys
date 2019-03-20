"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var types_1 = require("./util/types");
var _createElement = function (tag) {
    return function (attrs) {
        if (attrs === void 0) { attrs = {}; }
        var children = [];
        for (var _i = 1; _i < arguments.length; _i++) {
            children[_i - 1] = arguments[_i];
        }
        var element = document.createElement(tag);
        for (var attr in attrs) {
            var value = attrs[attr];
            if (value == null || types_1.isBoolean(value) && !value)
                continue;
            if (attr === "class" && types_1.isArray(value)) {
                for (var _a = 0, _b = value; _a < _b.length; _a++) {
                    var cls = _b[_a];
                    if (cls != null)
                        element.classList.add(cls);
                }
                continue;
            }
            if (attr === "style" && types_1.isPlainObject(value)) {
                for (var prop in value) {
                    element.style[prop] = value[prop];
                }
                continue;
            }
            if (attr === "data" && types_1.isPlainObject(value)) {
                for (var key in value) {
                    element.dataset[key] = value[key]; // XXX: attrs needs a better type
                }
                continue;
            }
            element.setAttribute(attr, value);
        }
        function append(child) {
            if (child instanceof HTMLElement)
                element.appendChild(child);
            else if (types_1.isString(child))
                element.appendChild(document.createTextNode(child));
            else if (child != null && child !== false)
                throw new Error("expected an HTMLElement, string, false or null, got " + JSON.stringify(child));
        }
        for (var _c = 0, children_1 = children; _c < children_1.length; _c++) {
            var child = children_1[_c];
            if (types_1.isArray(child)) {
                for (var _d = 0, child_1 = child; _d < child_1.length; _d++) {
                    var _child = child_1[_d];
                    append(_child);
                }
            }
            else
                append(child);
        }
        return element;
    };
};
function createElement(tag, attrs) {
    var children = [];
    for (var _i = 2; _i < arguments.length; _i++) {
        children[_i - 2] = arguments[_i];
    }
    return _createElement(tag).apply(void 0, [attrs].concat(children));
}
exports.createElement = createElement;
exports.div = _createElement("div"), exports.span = _createElement("span"), exports.link = _createElement("link"), exports.style = _createElement("style"), exports.a = _createElement("a"), exports.p = _createElement("p"), exports.i = _createElement("i"), exports.pre = _createElement("pre"), exports.button = _createElement("button"), exports.label = _createElement("label"), exports.input = _createElement("input"), exports.select = _createElement("select"), exports.option = _createElement("option"), exports.optgroup = _createElement("optgroup"), exports.textarea = _createElement("textarea"), exports.canvas = _createElement("canvas"), exports.ul = _createElement("ul"), exports.ol = _createElement("ol"), exports.li = _createElement("li");
exports.nbsp = document.createTextNode("\u00a0");
function removeElement(element) {
    var parent = element.parentNode;
    if (parent != null) {
        parent.removeChild(element);
    }
}
exports.removeElement = removeElement;
function replaceWith(element, replacement) {
    var parent = element.parentNode;
    if (parent != null) {
        parent.replaceChild(replacement, element);
    }
}
exports.replaceWith = replaceWith;
function prepend(element) {
    var nodes = [];
    for (var _i = 1; _i < arguments.length; _i++) {
        nodes[_i - 1] = arguments[_i];
    }
    var first = element.firstChild;
    for (var _a = 0, nodes_1 = nodes; _a < nodes_1.length; _a++) {
        var node = nodes_1[_a];
        element.insertBefore(node, first);
    }
}
exports.prepend = prepend;
function empty(element) {
    var child;
    while (child = element.firstChild) {
        element.removeChild(child);
    }
}
exports.empty = empty;
function show(element) {
    element.style.display = "";
}
exports.show = show;
function hide(element) {
    element.style.display = "none";
}
exports.hide = hide;
function position(element) {
    return {
        top: element.offsetTop,
        left: element.offsetLeft,
    };
}
exports.position = position;
function offset(element) {
    var rect = element.getBoundingClientRect();
    return {
        top: rect.top + window.pageYOffset - document.documentElement.clientTop,
        left: rect.left + window.pageXOffset - document.documentElement.clientLeft,
    };
}
exports.offset = offset;
function matches(el, selector) {
    var p = Element.prototype;
    var f = p.matches || p.webkitMatchesSelector || p.mozMatchesSelector || p.msMatchesSelector;
    return f.call(el, selector);
}
exports.matches = matches;
function parent(el, selector) {
    var node = el;
    while (node = node.parentElement) {
        if (matches(node, selector))
            return node;
    }
    return null;
}
exports.parent = parent;
function margin(el) {
    var style = getComputedStyle(el);
    return {
        top: parseFloat(style.marginTop) || 0,
        bottom: parseFloat(style.marginBottom) || 0,
        left: parseFloat(style.marginLeft) || 0,
        right: parseFloat(style.marginRight) || 0,
    };
}
exports.margin = margin;
function padding(el) {
    var style = getComputedStyle(el);
    return {
        top: parseFloat(style.paddingTop) || 0,
        bottom: parseFloat(style.paddingBottom) || 0,
        left: parseFloat(style.paddingLeft) || 0,
        right: parseFloat(style.paddingRight) || 0,
    };
}
exports.padding = padding;
var Keys;
(function (Keys) {
    Keys[Keys["Backspace"] = 8] = "Backspace";
    Keys[Keys["Tab"] = 9] = "Tab";
    Keys[Keys["Enter"] = 13] = "Enter";
    Keys[Keys["Esc"] = 27] = "Esc";
    Keys[Keys["PageUp"] = 33] = "PageUp";
    Keys[Keys["PageDown"] = 34] = "PageDown";
    Keys[Keys["Left"] = 37] = "Left";
    Keys[Keys["Up"] = 38] = "Up";
    Keys[Keys["Right"] = 39] = "Right";
    Keys[Keys["Down"] = 40] = "Down";
    Keys[Keys["Delete"] = 46] = "Delete";
})(Keys = exports.Keys || (exports.Keys = {}));
