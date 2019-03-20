"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var logging_1 = require("core/logging");
var document_1 = require("document");
var message_1 = require("protocol/message");
var ClientSession = /** @class */ (function () {
    function ClientSession(_connection, document /*Document*/, id) {
        var _this = this;
        this._connection = _connection;
        this.document = document;
        this.id = id;
        this._document_listener = function (event) { return _this._document_changed(event); };
        this.document.on_change(this._document_listener);
        this.event_manager = this.document.event_manager;
        this.event_manager.session = this;
    }
    ClientSession.prototype.handle = function (message) {
        var msgtype = message.msgtype();
        if (msgtype === 'PATCH-DOC')
            this._handle_patch(message);
        else if (msgtype === 'OK')
            this._handle_ok(message);
        else if (msgtype === 'ERROR')
            this._handle_error(message);
        else
            logging_1.logger.debug("Doing nothing with message " + message.msgtype());
    };
    ClientSession.prototype.close = function () {
        this._connection.close();
    };
    ClientSession.prototype.send_event = function (event) {
        var message = message_1.Message.create('EVENT', {}, JSON.stringify(event));
        this._connection.send(message);
    };
    /*protected*/ ClientSession.prototype._connection_closed = function () {
        this.document.remove_on_change(this._document_listener);
    };
    // Sends a request to the server for info about the server, such as its Bokeh
    // version. Returns a promise, the value of the promise is a free-form dictionary
    // of server details.
    ClientSession.prototype.request_server_info = function () {
        var message = message_1.Message.create('SERVER-INFO-REQ', {});
        var promise = this._connection.send_with_reply(message);
        return promise.then(function (reply) { return reply.content; });
    };
    // Sends some request to the server (no guarantee about which one) and returns
    // a promise which is completed when the server replies. The purpose of this
    // is that if you wait for the promise to be completed, you know the server
    // has processed the request. This is useful when writing tests because once
    // the server has processed this request it should also have processed any
    // events or requests you sent previously, which means you can check for the
    // results of that processing without a race condition. (This assumes the
    // server processes events in sequence, which it mostly has to semantically,
    // since reordering events might change the final state.)
    ClientSession.prototype.force_roundtrip = function () {
        return this.request_server_info().then(function (_) { return undefined; });
    };
    ClientSession.prototype._document_changed = function (event) {
        // Filter out events that were initiated by the ClientSession itself
        if (event.setter_id === this.id)
            return;
        // Filter out changes to attributes that aren't server-visible
        if (event instanceof document_1.ModelChangedEvent && !(event.attr in event.model.serializable_attributes()))
            return;
        // TODO (havocp) the connection may be closed here, which will
        // cause this send to throw an error - need to deal with it more cleanly.
        var message = message_1.Message.create('PATCH-DOC', {}, this.document.create_json_patch([event]));
        this._connection.send(message);
    };
    ClientSession.prototype._handle_patch = function (message) {
        this.document.apply_json_patch(message.content, message.buffers, this.id);
    };
    ClientSession.prototype._handle_ok = function (message) {
        logging_1.logger.trace("Unhandled OK reply to " + message.reqid());
    };
    ClientSession.prototype._handle_error = function (message) {
        logging_1.logger.error("Unhandled ERROR reply to " + message.reqid() + ": " + message.content['text']);
    };
    return ClientSession;
}());
exports.ClientSession = ClientSession;
