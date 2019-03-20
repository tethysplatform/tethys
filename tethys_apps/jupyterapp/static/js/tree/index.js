"use strict";
function is_browser() {
    return typeof window !== "undefined" && typeof window.document !== "undefined";
}
function bokehjs() {
    if (!is_browser()) {
        throw new Error("bokehjs requires a window with a document. If your runtime environment doesn't provide those, e.g. pure node.js, you can use jsdom library to configure window and document.");
    }
    var Bokeh = require('./main');
    return Bokeh;
}
module.exports = is_browser() ? bokehjs() : bokehjs;
