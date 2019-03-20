"use strict";
//     Underscore.js 1.8.3
//     http://underscorejs.org
//     (c) 2009-2015 Jeremy Ashkenas, DocumentCloud and Investigative Reporters & Editors
//     Underscore may be freely distributed under the MIT license.
Object.defineProperty(exports, "__esModule", { value: true });
function delay(func, wait) {
    return setTimeout(func, wait);
}
exports.delay = delay;
var _defer = typeof requestAnimationFrame === "function" ? requestAnimationFrame : setImmediate;
function defer(func) {
    return _defer(func);
}
exports.defer = defer;
function throttle(func, wait, options) {
    if (options === void 0) { options = {}; }
    var context, args, result;
    var timeout = null;
    var previous = 0;
    var later = function () {
        previous = options.leading === false ? 0 : Date.now();
        timeout = null;
        result = func.apply(context, args);
        if (!timeout)
            context = args = null;
    };
    return function () {
        var now = Date.now();
        if (!previous && options.leading === false)
            previous = now;
        var remaining = wait - (now - previous);
        context = this;
        args = arguments;
        if (remaining <= 0 || remaining > wait) {
            if (timeout) {
                clearTimeout(timeout);
                timeout = null;
            }
            previous = now;
            result = func.apply(context, args);
            if (!timeout)
                context = args = null;
        }
        else if (!timeout && options.trailing !== false) {
            timeout = setTimeout(later, remaining);
        }
        return result;
    };
}
exports.throttle = throttle;
function once(func) {
    var done = false;
    var memo;
    return function () {
        if (!done) {
            done = true;
            memo = func();
        }
        return memo;
    };
}
exports.once = once;
