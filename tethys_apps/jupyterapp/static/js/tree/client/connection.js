"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var es6_promise_1 = require("es6-promise");
var logging_1 = require("core/logging");
var document_1 = require("document");
var message_1 = require("protocol/message");
var receiver_1 = require("protocol/receiver");
var session_1 = require("./session");
exports.DEFAULT_SERVER_WEBSOCKET_URL = "ws://localhost:5006/ws";
exports.DEFAULT_SESSION_ID = "default";
var _connection_count = 0;
var ClientConnection = /** @class */ (function () {
    function ClientConnection(url, id, args_string, _on_have_session_hook, _on_closed_permanently_hook) {
        if (url === void 0) { url = exports.DEFAULT_SERVER_WEBSOCKET_URL; }
        if (id === void 0) { id = exports.DEFAULT_SESSION_ID; }
        if (args_string === void 0) { args_string = null; }
        if (_on_have_session_hook === void 0) { _on_have_session_hook = null; }
        if (_on_closed_permanently_hook === void 0) { _on_closed_permanently_hook = null; }
        this.url = url;
        this.id = id;
        this.args_string = args_string;
        this._on_have_session_hook = _on_have_session_hook;
        this._on_closed_permanently_hook = _on_closed_permanently_hook;
        this._number = _connection_count++;
        this.socket = null;
        this.session = null;
        this.closed_permanently = false;
        this._current_handler = null;
        this._pending_ack = null; // null or [resolve,reject]
        this._pending_replies = {}; // map reqid to [resolve,reject]
        this._receiver = new receiver_1.Receiver();
        logging_1.logger.debug("Creating websocket " + this._number + " to '" + this.url + "' session '" + this.id + "'");
    }
    ClientConnection.prototype.connect = function () {
        var _this = this;
        if (this.closed_permanently)
            return es6_promise_1.Promise.reject(new Error("Cannot connect() a closed ClientConnection"));
        if (this.socket != null)
            return es6_promise_1.Promise.reject(new Error("Already connected"));
        this._pending_replies = {};
        this._current_handler = null;
        try {
            var versioned_url = this.url + "?bokeh-protocol-version=1.0&bokeh-session-id=" + this.id;
            if (this.args_string != null && this.args_string.length > 0)
                versioned_url += "&" + this.args_string;
            this.socket = new WebSocket(versioned_url);
            return new es6_promise_1.Promise(function (resolve, reject) {
                // "arraybuffer" gives us binary data we can look at;
                // if we just needed an opaque blob we could use "blob"
                _this.socket.binaryType = "arraybuffer";
                _this.socket.onopen = function () { return _this._on_open(resolve, reject); };
                _this.socket.onmessage = function (event) { return _this._on_message(event); };
                _this.socket.onclose = function (event) { return _this._on_close(event); };
                _this.socket.onerror = function () { return _this._on_error(reject); };
            });
        }
        catch (error) {
            logging_1.logger.error("websocket creation failed to url: " + this.url);
            logging_1.logger.error(" - " + error);
            return es6_promise_1.Promise.reject(error);
        }
    };
    ClientConnection.prototype.close = function () {
        if (!this.closed_permanently) {
            logging_1.logger.debug("Permanently closing websocket connection " + this._number);
            this.closed_permanently = true;
            if (this.socket != null)
                this.socket.close(1000, "close method called on ClientConnection " + this._number);
            this.session._connection_closed();
            if (this._on_closed_permanently_hook != null) {
                this._on_closed_permanently_hook();
                this._on_closed_permanently_hook = null;
            }
        }
    };
    ClientConnection.prototype._schedule_reconnect = function (milliseconds) {
        var _this = this;
        var retry = function () {
            // TODO commented code below until we fix reconnection to repull
            // the document when required. Otherwise, we get a lot of
            // confusing errors that are causing trouble when debugging.
            /*
            if (this.closed_permanently) {
            */
            if (!_this.closed_permanently)
                logging_1.logger.info("Websocket connection " + _this._number + " disconnected, will not attempt to reconnect");
            return;
            /*
            } else {
              logger.debug(`Attempting to reconnect websocket ${this._number}`)
              this.connect()
            }
            */
        };
        setTimeout(retry, milliseconds);
    };
    ClientConnection.prototype.send = function (message) {
        if (this.socket == null)
            throw new Error("not connected so cannot send " + message);
        message.send(this.socket);
    };
    ClientConnection.prototype.send_with_reply = function (message) {
        var _this = this;
        var promise = new es6_promise_1.Promise(function (resolve, reject) {
            _this._pending_replies[message.msgid()] = [resolve, reject];
            _this.send(message);
        });
        return promise.then(function (message) {
            if (message.msgtype() === "ERROR")
                throw new Error("Error reply " + message.content['text']);
            else
                return message;
        }, function (error) {
            throw error;
        });
    };
    ClientConnection.prototype._pull_doc_json = function () {
        var message = message_1.Message.create("PULL-DOC-REQ", {});
        var promise = this.send_with_reply(message);
        return promise.then(function (reply) {
            if (!('doc' in reply.content))
                throw new Error("No 'doc' field in PULL-DOC-REPLY");
            return reply.content['doc'];
        }, function (error) {
            throw error;
        });
    };
    ClientConnection.prototype._repull_session_doc = function () {
        var _this = this;
        if (this.session == null)
            logging_1.logger.debug("Pulling session for first time");
        else
            logging_1.logger.debug("Repulling session");
        this._pull_doc_json().then(function (doc_json) {
            if (_this.session == null) {
                if (_this.closed_permanently)
                    logging_1.logger.debug("Got new document after connection was already closed");
                else {
                    var document_2 = document_1.Document.from_json(doc_json);
                    // Constructing models changes some of their attributes, we deal with that
                    // here. This happens when models set attributes during construction
                    // or initialization.
                    var patch = document_1.Document._compute_patch_since_json(doc_json, document_2);
                    if (patch.events.length > 0) {
                        logging_1.logger.debug("Sending " + patch.events.length + " changes from model construction back to server");
                        var patch_message = message_1.Message.create('PATCH-DOC', {}, patch);
                        _this.send(patch_message);
                    }
                    _this.session = new session_1.ClientSession(_this, document_2, _this.id);
                    logging_1.logger.debug("Created a new session from new pulled doc");
                    if (_this._on_have_session_hook != null) {
                        _this._on_have_session_hook(_this.session);
                        _this._on_have_session_hook = null;
                    }
                }
            }
            else {
                _this.session.document.replace_with_json(doc_json);
                logging_1.logger.debug("Updated existing session with new pulled doc");
            }
        }, function (error) {
            // handling the error here is useless because we wouldn't
            // get errors from the resolve handler above, so see
            // the catch below instead
            throw error;
        }).catch(function (error) {
            if (console.trace != null)
                console.trace(error);
            logging_1.logger.error("Failed to repull session " + error);
        });
    };
    ClientConnection.prototype._on_open = function (resolve, reject) {
        var _this = this;
        logging_1.logger.info("Websocket connection " + this._number + " is now open");
        this._pending_ack = [resolve, reject];
        this._current_handler = function (message) {
            _this._awaiting_ack_handler(message);
        };
    };
    ClientConnection.prototype._on_message = function (event) {
        if (this._current_handler == null)
            logging_1.logger.error("Got a message with no current handler set");
        try {
            this._receiver.consume(event.data);
        }
        catch (e) {
            this._close_bad_protocol(e.toString());
        }
        if (this._receiver.message == null)
            return;
        var msg = this._receiver.message;
        var problem = msg.problem();
        if (problem != null)
            this._close_bad_protocol(problem);
        this._current_handler(msg);
    };
    ClientConnection.prototype._on_close = function (event) {
        var _this = this;
        logging_1.logger.info("Lost websocket " + this._number + " connection, " + event.code + " (" + event.reason + ")");
        this.socket = null;
        if (this._pending_ack != null) {
            this._pending_ack[1](new Error("Lost websocket connection, " + event.code + " (" + event.reason + ")"));
            this._pending_ack = null;
        }
        var pop_pending = function () {
            for (var reqid in _this._pending_replies) {
                var promise_funcs_1 = _this._pending_replies[reqid];
                delete _this._pending_replies[reqid];
                return promise_funcs_1;
            }
            return null;
        };
        var promise_funcs = pop_pending();
        while (promise_funcs != null) {
            promise_funcs[1]("Disconnected");
            promise_funcs = pop_pending();
        }
        if (!this.closed_permanently)
            this._schedule_reconnect(2000);
    };
    ClientConnection.prototype._on_error = function (reject) {
        logging_1.logger.debug("Websocket error on socket " + this._number);
        reject(new Error("Could not open websocket"));
    };
    ClientConnection.prototype._close_bad_protocol = function (detail) {
        logging_1.logger.error("Closing connection: " + detail);
        if (this.socket != null)
            this.socket.close(1002, detail); // 1002 = protocol error
    };
    ClientConnection.prototype._awaiting_ack_handler = function (message) {
        var _this = this;
        if (message.msgtype() === "ACK") {
            this._current_handler = function (message) { return _this._steady_state_handler(message); };
            // Reload any sessions
            // TODO (havocp) there's a race where we might get a PATCH before
            // we send and get a reply to our pulls.
            this._repull_session_doc();
            if (this._pending_ack != null) {
                this._pending_ack[0](this);
                this._pending_ack = null;
            }
        }
        else
            this._close_bad_protocol("First message was not an ACK");
    };
    ClientConnection.prototype._steady_state_handler = function (message) {
        if (message.reqid() in this._pending_replies) {
            var promise_funcs = this._pending_replies[message.reqid()];
            delete this._pending_replies[message.reqid()];
            promise_funcs[0](message);
        }
        else
            this.session.handle(message);
    };
    return ClientConnection;
}());
exports.ClientConnection = ClientConnection;
// Returns a promise of a ClientSession
// The returned promise has a close() method in case you want to close before
// getting a session; session.close() works too once you have a session.
function pull_session(url, session_id, args_string) {
    var connection;
    var promise = new es6_promise_1.Promise(function (resolve, reject) {
        connection = new ClientConnection(url, session_id, args_string, function (session) {
            try {
                resolve(session);
            }
            catch (error) {
                logging_1.logger.error("Promise handler threw an error, closing session " + error);
                session.close();
                throw error;
            }
        }, function () {
            // we rely on reject() as a no-op if we already resolved
            reject(new Error("Connection was closed before we successfully pulled a session"));
        });
        return connection.connect().then(function (_) { return undefined; }, function (error) {
            logging_1.logger.error("Failed to connect to Bokeh server " + error);
            throw error;
        });
    });
    /*
    // add a "close" method to the promise... too weird?
    promise.close = () => {
      connection.close()
    }
    */
    return promise;
}
exports.pull_session = pull_session;
