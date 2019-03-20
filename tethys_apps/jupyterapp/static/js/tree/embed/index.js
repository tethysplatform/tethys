"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var document_1 = require("../document");
var logging_1 = require("../core/logging");
var callback_1 = require("../core/util/callback");
var string_1 = require("../core/util/string");
var types_1 = require("../core/util/types");
var standalone_1 = require("./standalone");
var server_1 = require("./server");
var dom_1 = require("./dom");
var standalone_2 = require("./standalone");
exports.add_document_standalone = standalone_2.add_document_standalone;
var server_2 = require("./server");
exports.add_document_from_session = server_2.add_document_from_session;
var notebook_1 = require("./notebook");
exports.embed_items_notebook = notebook_1.embed_items_notebook;
exports.kernels = notebook_1.kernels;
var dom_2 = require("./dom");
exports.BOKEH_ROOT = dom_2.BOKEH_ROOT;
exports.inject_css = dom_2.inject_css;
exports.inject_raw_css = dom_2.inject_raw_css;
function embed_item(item, target_id) {
    var _a;
    var docs_json = {};
    var doc_id = string_1.uuid4();
    docs_json[doc_id] = item.doc;
    if (target_id == null)
        target_id = item.target_id;
    var roots = (_a = {}, _a[item.root_id] = target_id, _a);
    var render_item = { roots: roots, docid: doc_id };
    callback_1.defer(function () { return _embed_items(docs_json, [render_item]); });
}
exports.embed_item = embed_item;
// TODO (bev) this is currently clunky. Standalone embeds only provide
// the first two args, whereas server provide the app_app, and *may* prove and
// absolute_url as well if non-relative links are needed for resources. This function
// should probably be split in to two pieces to reflect the different usage patterns
function embed_items(docs_json, render_items, app_path, absolute_url) {
    callback_1.defer(function () { return _embed_items(docs_json, render_items, app_path, absolute_url); });
}
exports.embed_items = embed_items;
function _embed_items(docs_json, render_items, app_path, absolute_url) {
    if (types_1.isString(docs_json))
        docs_json = JSON.parse(string_1.unescape(docs_json));
    var docs = {};
    for (var docid in docs_json) {
        var doc_json = docs_json[docid];
        docs[docid] = document_1.Document.from_json(doc_json);
    }
    for (var _i = 0, render_items_1 = render_items; _i < render_items_1.length; _i++) {
        var item = render_items_1[_i];
        var element = dom_1._resolve_element(item);
        var roots = dom_1._resolve_root_elements(item);
        if (item.docid != null) {
            standalone_1.add_document_standalone(docs[item.docid], element, roots, item.use_for_title);
        }
        else if (item.sessionid != null) {
            var websocket_url = server_1._get_ws_url(app_path, absolute_url);
            logging_1.logger.debug("embed: computed ws url: " + websocket_url);
            var promise = server_1.add_document_from_session(websocket_url, item.sessionid, element, roots, item.use_for_title);
            promise.then(function () {
                console.log("Bokeh items were rendered successfully");
            }, function (error) {
                console.log("Error rendering Bokeh items:", error);
            });
        }
        else
            throw new Error("Error rendering Bokeh items: either 'docid' or 'sessionid' was expected.");
    }
}
