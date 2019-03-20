"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var AssertionError = /** @class */ (function (_super) {
    tslib_1.__extends(AssertionError, _super);
    function AssertionError() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return AssertionError;
}(Error));
exports.AssertionError = AssertionError;
function assert(condition, message) {
    if (condition === true || (condition !== false && condition()))
        return;
    throw new AssertionError(message || "Assertion failed");
}
exports.assert = assert;
