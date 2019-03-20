"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var document_1 = require("../document");
var receiver_1 = require("../protocol/receiver");
var logging_1 = require("../core/logging");
var object_1 = require("../core/util/object");
var standalone_1 = require("./standalone");
var dom_1 = require("./dom");
// This exists to allow the jupyterlab_bokeh extension to store the
// notebook kernel so that _init_comms can register the comms target.
// This has to be available at window.Bokeh.embed.kernels in JupyterLab
exports.kernels = {};
function _handle_notebook_comms(receiver, comm_msg) {
    if (comm_msg.buffers.length > 0)
        receiver.consume(comm_msg.buffers[0].buffer);
    else
        receiver.consume(comm_msg.content.data);
    var msg = receiver.message;
    if (msg != null)
        this.apply_json_patch(msg.content, msg.buffers);
}
function _init_comms(target, doc) {
    if (typeof Jupyter !== 'undefined' && Jupyter.notebook.kernel != null) {
        logging_1.logger.info("Registering Jupyter comms for target " + target);
        var comm_manager = Jupyter.notebook.kernel.comm_manager;
        try {
            comm_manager.register_target(target, function (comm) {
                logging_1.logger.info("Registering Jupyter comms for target " + target);
                var r = new receiver_1.Receiver();
                comm.on_msg(_handle_notebook_comms.bind(doc, r));
            });
        }
        catch (e) {
            logging_1.logger.warn("Jupyter comms failed to register. push_notebook() will not function. (exception reported: " + e + ")");
        }
    }
    else if (doc.roots()[0].id in exports.kernels) {
        logging_1.logger.info("Registering JupyterLab comms for target " + target);
        var kernel = exports.kernels[doc.roots()[0].id];
        try {
            kernel.registerCommTarget(target, function (comm) {
                logging_1.logger.info("Registering JupyterLab comms for target " + target);
                var r = new receiver_1.Receiver();
                comm.onMsg = _handle_notebook_comms.bind(doc, r);
            });
        }
        catch (e) {
            logging_1.logger.warn("Jupyter comms failed to register. push_notebook() will not function. (exception reported: " + e + ")");
        }
    }
    else {
        console.warn("Jupyter notebooks comms not available. push_notebook() will not function. If running JupyterLab ensure the latest jupyterlab_bokeh extension is installed. In an exported notebook this warning is expected.");
    }
}
function embed_items_notebook(docs_json, render_items) {
    if (object_1.size(docs_json) != 1)
        throw new Error("embed_items_notebook expects exactly one document in docs_json");
    var document = document_1.Document.from_json(object_1.values(docs_json)[0]);
    for (var _i = 0, render_items_1 = render_items; _i < render_items_1.length; _i++) {
        var item = render_items_1[_i];
        if (item.notebook_comms_target != null)
            _init_comms(item.notebook_comms_target, document);
        var element = dom_1._resolve_element(item);
        var roots = dom_1._resolve_root_elements(item);
        standalone_1.add_document_standalone(document, element, roots);
    }
}
exports.embed_items_notebook = embed_items_notebook;
