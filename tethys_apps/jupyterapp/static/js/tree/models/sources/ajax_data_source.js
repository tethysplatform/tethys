"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var remote_data_source_1 = require("./remote_data_source");
var logging_1 = require("core/logging");
var p = require("core/properties");
var AjaxDataSource = /** @class */ (function (_super) {
    tslib_1.__extends(AjaxDataSource, _super);
    function AjaxDataSource(attrs) {
        var _this = _super.call(this, attrs) || this;
        _this.initialized = false;
        return _this;
    }
    AjaxDataSource.initClass = function () {
        this.prototype.type = 'AjaxDataSource';
        this.define({
            mode: [p.String, 'replace'],
            content_type: [p.String, 'application/json'],
            http_headers: [p.Any, {}],
            max_size: [p.Number],
            method: [p.String, 'POST'],
            if_modified: [p.Bool, false],
        });
    };
    AjaxDataSource.prototype.destroy = function () {
        if (this.interval != null)
            clearInterval(this.interval);
        _super.prototype.destroy.call(this);
    };
    AjaxDataSource.prototype.setup = function () {
        var _this = this;
        if (!this.initialized) {
            this.initialized = true;
            this.get_data(this.mode);
            if (this.polling_interval) {
                var callback = function () { return _this.get_data(_this.mode, _this.max_size, _this.if_modified); };
                this.interval = setInterval(callback, this.polling_interval);
            }
        }
    };
    AjaxDataSource.prototype.get_data = function (mode, max_size, _if_modified) {
        var _this = this;
        if (max_size === void 0) { max_size = 0; }
        if (_if_modified === void 0) { _if_modified = false; }
        var xhr = this.prepare_request();
        // TODO: if_modified
        xhr.addEventListener("load", function () { return _this.do_load(xhr, mode, max_size); });
        xhr.addEventListener("error", function () { return _this.do_error(xhr); });
        xhr.send();
    };
    AjaxDataSource.prototype.prepare_request = function () {
        var xhr = new XMLHttpRequest();
        xhr.open(this.method, this.data_url, true);
        xhr.withCredentials = false;
        xhr.setRequestHeader("Content-Type", this.content_type);
        var http_headers = this.http_headers;
        for (var name_1 in http_headers) {
            var value = http_headers[name_1];
            xhr.setRequestHeader(name_1, value);
        }
        return xhr;
    };
    AjaxDataSource.prototype.do_load = function (xhr, mode, max_size) {
        if (xhr.status === 200) {
            var data = JSON.parse(xhr.responseText);
            switch (mode) {
                case "replace": {
                    this.data = data;
                    break;
                }
                case "append": {
                    var original_data = this.data;
                    for (var _i = 0, _a = this.columns(); _i < _a.length; _i++) {
                        var column = _a[_i];
                        // XXX: support typed arrays
                        var old_col = Array.from(original_data[column]);
                        var new_col = Array.from(data[column]);
                        data[column] = old_col.concat(new_col).slice(-max_size);
                    }
                    this.data = data;
                    break;
                }
            }
        }
    };
    AjaxDataSource.prototype.do_error = function (xhr) {
        logging_1.logger.error("Failed to fetch JSON from " + this.data_url + " with code " + xhr.status);
    };
    return AjaxDataSource;
}(remote_data_source_1.RemoteDataSource));
exports.AjaxDataSource = AjaxDataSource;
AjaxDataSource.initClass();
