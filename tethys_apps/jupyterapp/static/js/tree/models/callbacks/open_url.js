"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var callback_1 = require("./callback");
var p = require("core/properties");
var selection_1 = require("core/util/selection");
var templating_1 = require("core/util/templating");
var OpenURL = /** @class */ (function (_super) {
    tslib_1.__extends(OpenURL, _super);
    function OpenURL(attrs) {
        return _super.call(this, attrs) || this;
    }
    OpenURL.initClass = function () {
        this.prototype.type = 'OpenURL';
        this.define({
            url: [p.String, 'http://'],
        });
    };
    OpenURL.prototype.execute = function (_cb_obj, cb_data) {
        for (var _i = 0, _a = selection_1.get_indices(cb_data.source); _i < _a.length; _i++) {
            var i = _a[_i];
            var url = templating_1.replace_placeholders(this.url, cb_data.source, i);
            window.open(url);
        }
        return null;
    };
    return OpenURL;
}(callback_1.Callback));
exports.OpenURL = OpenURL;
OpenURL.initClass();
