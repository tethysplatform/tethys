"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
// Just a dumb key/value record for collecting arbitrary info for tests
exports.results = {};
// Selenium has race conditions that make it difficult to read out the
// results structure. This function deletes/creates a div that can act as
// a semaphore. Tests should wait for the previous div to be stale, then
// find the new div. At that point the results should be available
function _update_test_div() {
    var body = document.getElementsByTagName("body")[0];
    var col = document.getElementsByClassName("bokeh-test-div");
    if (col.length == 1)
        body.removeChild(col[0]);
    delete col[0];
    var box = document.createElement("div");
    box.classList.add("bokeh-test-div");
    box.style.display = "none";
    body.insertBefore(box, body.firstChild);
}
function init() {
    _update_test_div();
}
exports.init = init;
function record(key, value) {
    exports.results[key] = value;
    _update_test_div();
}
exports.record = record;
function count(key) {
    if (exports.results[key] == undefined)
        exports.results[key] = 0;
    exports.results[key] += 1;
    _update_test_div();
}
exports.count = count;
function clear() {
    for (var _i = 0, _a = Object.keys(exports.results); _i < _a.length; _i++) {
        var prop = _a[_i];
        delete exports.results[prop];
    }
    _update_test_div();
}
exports.clear = clear;
