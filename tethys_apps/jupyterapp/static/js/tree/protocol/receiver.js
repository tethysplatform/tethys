"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var message_1 = require("protocol/message");
var Receiver = /** @class */ (function () {
    function Receiver() {
        this.message = null;
        this._partial = null;
        this._fragments = [];
        this._buf_header = null;
        this._current_consumer = this._HEADER;
    }
    Receiver.prototype.consume = function (fragment) {
        this._current_consumer(fragment);
    };
    Receiver.prototype._HEADER = function (fragment) {
        this._assume_text(fragment);
        this.message = null;
        this._partial = null;
        this._fragments = [fragment];
        this._buf_header = null;
        this._current_consumer = this._METADATA;
    };
    Receiver.prototype._METADATA = function (fragment) {
        this._assume_text(fragment);
        this._fragments.push(fragment);
        this._current_consumer = this._CONTENT;
    };
    Receiver.prototype._CONTENT = function (fragment) {
        this._assume_text(fragment);
        this._fragments.push(fragment);
        var _a = this._fragments.slice(0, 3), header_json = _a[0], metadata_json = _a[1], content_json = _a[2];
        this._partial = message_1.Message.assemble(header_json, metadata_json, content_json);
        this._check_complete();
    };
    Receiver.prototype._BUFFER_HEADER = function (fragment) {
        this._assume_text(fragment);
        this._buf_header = fragment; // XXX: assume text but Header is expected
        this._current_consumer = this._BUFFER_PAYLOAD;
    };
    Receiver.prototype._BUFFER_PAYLOAD = function (fragment) {
        this._assume_binary(fragment);
        this._partial.assemble_buffer(this._buf_header, fragment);
        this._check_complete();
    };
    Receiver.prototype._assume_text = function (fragment) {
        if (fragment instanceof ArrayBuffer)
            throw new Error("Expected text fragment but received binary fragment");
    };
    Receiver.prototype._assume_binary = function (fragment) {
        if (!(fragment instanceof ArrayBuffer))
            throw new Error("Expected binary fragment but received text fragment");
    };
    Receiver.prototype._check_complete = function () {
        if (this._partial.complete()) {
            this.message = this._partial;
            this._current_consumer = this._HEADER;
        }
        else
            this._current_consumer = this._BUFFER_HEADER;
    };
    return Receiver;
}());
exports.Receiver = Receiver;
