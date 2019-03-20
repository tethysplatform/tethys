"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var string_1 = require("core/util/string");
var Message = /** @class */ (function () {
    function Message(header, metadata, content) {
        this.header = header;
        this.metadata = metadata;
        this.content = content;
        this.buffers = [];
    }
    Message.assemble = function (header_json, metadata_json, content_json) {
        var header = JSON.parse(header_json);
        var metadata = JSON.parse(metadata_json);
        var content = JSON.parse(content_json);
        return new Message(header, metadata, content);
    };
    Message.prototype.assemble_buffer = function (buf_header, buf_payload) {
        var nb = this.header.num_buffers != null ? this.header.num_buffers : 0;
        if (nb <= this.buffers.length)
            throw new Error("too many buffers received, expecting #{nb}");
        this.buffers.push([buf_header, buf_payload]);
    };
    // not defined for BokehJS, only *receiving* buffers is supported
    // add_buffer: (buf_header, buf_payload) ->
    // write_buffers: (socket)
    Message.create = function (msgtype, metadata, content) {
        if (content === void 0) { content = {}; }
        var header = Message.create_header(msgtype);
        return new Message(header, metadata, content);
    };
    Message.create_header = function (msgtype) {
        return {
            msgid: string_1.uniqueId(),
            msgtype: msgtype,
        };
    };
    Message.prototype.complete = function () {
        if (this.header != null && this.metadata != null && this.content != null) {
            if ('num_buffers' in this.header)
                return this.buffers.length === this.header.num_buffers;
            else
                return true;
        }
        else
            return false;
    };
    Message.prototype.send = function (socket) {
        var nb = this.header.num_buffers != null ? this.header.num_buffers : 0;
        if (nb > 0)
            throw new Error("BokehJS only supports receiving buffers, not sending");
        var header_json = JSON.stringify(this.header);
        var metadata_json = JSON.stringify(this.metadata);
        var content_json = JSON.stringify(this.content);
        socket.send(header_json);
        socket.send(metadata_json);
        socket.send(content_json);
    };
    Message.prototype.msgid = function () {
        return this.header.msgid;
    };
    Message.prototype.msgtype = function () {
        return this.header.msgtype;
    };
    Message.prototype.reqid = function () {
        return this.header.reqid;
    };
    // return the reason we should close on bad protocol, if there is one
    Message.prototype.problem = function () {
        if (!('msgid' in this.header))
            return "No msgid in header";
        else if (!('msgtype' in this.header))
            return "No msgtype in header";
        else
            return null;
    };
    return Message;
}());
exports.Message = Message;
