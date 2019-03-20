"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var connection_1 = require("../client/connection");
var logging_1 = require("../core/logging");
var standalone_1 = require("./standalone");
// @internal
function _get_ws_url(app_path, absolute_url) {
    var protocol = 'ws:';
    if (window.location.protocol == 'https:')
        protocol = 'wss:';
    var loc;
    if (absolute_url != null) {
        loc = document.createElement('a');
        loc.href = absolute_url;
    }
    else
        loc = window.location;
    if (app_path != null) {
        if (app_path == "/")
            app_path = "";
    }
    else
        app_path = loc.pathname.replace(/\/+$/, '');
    return protocol + '//' + loc.host + app_path + '/ws';
}
exports._get_ws_url = _get_ws_url;
// map { websocket url to map { session id to promise of ClientSession } }
var _sessions = {};
function _get_session(websocket_url, session_id, args_string) {
    if (!(websocket_url in _sessions))
        _sessions[websocket_url] = {};
    var subsessions = _sessions[websocket_url];
    if (!(session_id in subsessions))
        subsessions[session_id] = connection_1.pull_session(websocket_url, session_id, args_string);
    return subsessions[session_id];
}
// Fill element with the roots from session_id
function add_document_from_session(websocket_url, session_id, element, roots, use_for_title) {
    if (roots === void 0) { roots = {}; }
    if (use_for_title === void 0) { use_for_title = false; }
    var args_string = window.location.search.substr(1);
    var promise = _get_session(websocket_url, session_id, args_string);
    return promise.then(function (session) {
        return standalone_1.add_document_standalone(session.document, element, roots, use_for_title);
    }, function (error) {
        logging_1.logger.error("Failed to load Bokeh session " + session_id + ": " + error);
        throw error;
    });
}
exports.add_document_from_session = add_document_from_session;
