"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
function _delay_animation(callback) {
    callback(Date.now()); // XXX: performance.now()
    return -1;
}
var delay_animation = (typeof window !== 'undefined' ? window.requestAnimationFrame : undefined) ||
    (typeof window !== 'undefined' ? window.webkitRequestAnimationFrame : undefined) ||
    (typeof window !== 'undefined' ? window.mozRequestAnimationFrame : undefined) ||
    (typeof window !== 'undefined' ? window.msRequestAnimationFrame : undefined) || _delay_animation;
// Returns a function, that, when invoked, will only be triggered at
// most once during a given window of time.
//
// In addition, if the browser supports requestAnimationFrame, the
// throttled function will be run no more frequently than request
// animation frame allows.
//
// @param func [function] the function to throttle
// @param wait [number] time in milliseconds to use for window
// @return [function] throttled function
//
function throttle(func, wait) {
    var timeout = null;
    var previous = 0;
    var pending = false;
    var later = function () {
        previous = Date.now();
        timeout = null;
        pending = false;
        func();
    };
    return function () {
        var now = Date.now();
        var remaining = wait - (now - previous);
        if (remaining <= 0 && !pending) {
            if (timeout != null)
                clearTimeout(timeout);
            pending = true;
            delay_animation(later);
        }
        else if (!timeout && !pending)
            timeout = setTimeout(function () { return delay_animation(later); }, remaining);
    };
}
exports.throttle = throttle;
