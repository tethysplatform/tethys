"use strict";
// Based on https://github.com/phosphorjs/phosphor/blob/master/packages/signaling/src/index.ts
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var data_structures_1 = require("./util/data_structures");
var callback_1 = require("./util/callback");
var array_1 = require("./util/array");
var Signal = /** @class */ (function () {
    function Signal(sender, name) {
        this.sender = sender;
        this.name = name;
    }
    Signal.prototype.connect = function (slot, context) {
        if (context === void 0) { context = null; }
        if (!receiversForSender.has(this.sender)) {
            receiversForSender.set(this.sender, []);
        }
        var receivers = receiversForSender.get(this.sender);
        if (findConnection(receivers, this, slot, context) != null) {
            return false;
        }
        var receiver = context || slot;
        if (!sendersForReceiver.has(receiver)) {
            sendersForReceiver.set(receiver, []);
        }
        var senders = sendersForReceiver.get(receiver);
        var connection = { signal: this, slot: slot, context: context };
        receivers.push(connection);
        senders.push(connection);
        return true;
    };
    Signal.prototype.disconnect = function (slot, context) {
        if (context === void 0) { context = null; }
        var receivers = receiversForSender.get(this.sender);
        if (receivers == null || receivers.length === 0) {
            return false;
        }
        var connection = findConnection(receivers, this, slot, context);
        if (connection == null) {
            return false;
        }
        var receiver = context || slot;
        var senders = sendersForReceiver.get(receiver);
        connection.signal = null;
        scheduleCleanup(receivers);
        scheduleCleanup(senders);
        return true;
    };
    Signal.prototype.emit = function (args) {
        var receivers = receiversForSender.get(this.sender) || [];
        for (var _i = 0, receivers_1 = receivers; _i < receivers_1.length; _i++) {
            var _a = receivers_1[_i], signal = _a.signal, slot = _a.slot, context = _a.context;
            if (signal === this) {
                slot.call(context, args, this.sender);
            }
        }
    };
    return Signal;
}());
exports.Signal = Signal;
var Signal0 = /** @class */ (function (_super) {
    tslib_1.__extends(Signal0, _super);
    function Signal0() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    Signal0.prototype.emit = function () {
        _super.prototype.emit.call(this, undefined);
    };
    return Signal0;
}(Signal));
exports.Signal0 = Signal0;
(function (Signal) {
    function disconnectBetween(sender, receiver) {
        var receivers = receiversForSender.get(sender);
        if (receivers == null || receivers.length === 0)
            return;
        var senders = sendersForReceiver.get(receiver);
        if (senders == null || senders.length === 0)
            return;
        for (var _i = 0, senders_1 = senders; _i < senders_1.length; _i++) {
            var connection = senders_1[_i];
            if (connection.signal == null)
                return;
            if (connection.signal.sender === sender)
                connection.signal = null;
        }
        scheduleCleanup(receivers);
        scheduleCleanup(senders);
    }
    Signal.disconnectBetween = disconnectBetween;
    function disconnectSender(sender) {
        var receivers = receiversForSender.get(sender);
        if (receivers == null || receivers.length === 0)
            return;
        for (var _i = 0, receivers_2 = receivers; _i < receivers_2.length; _i++) {
            var connection = receivers_2[_i];
            if (connection.signal == null)
                return;
            var receiver = connection.context || connection.slot;
            connection.signal = null;
            scheduleCleanup(sendersForReceiver.get(receiver));
        }
        scheduleCleanup(receivers);
    }
    Signal.disconnectSender = disconnectSender;
    function disconnectReceiver(receiver) {
        var senders = sendersForReceiver.get(receiver);
        if (senders == null || senders.length === 0)
            return;
        for (var _i = 0, senders_2 = senders; _i < senders_2.length; _i++) {
            var connection = senders_2[_i];
            if (connection.signal == null)
                return;
            var sender = connection.signal.sender;
            connection.signal = null;
            scheduleCleanup(receiversForSender.get(sender));
        }
        scheduleCleanup(senders);
    }
    Signal.disconnectReceiver = disconnectReceiver;
    function disconnectAll(obj) {
        var receivers = receiversForSender.get(obj);
        if (receivers != null && receivers.length !== 0) {
            for (var _i = 0, receivers_3 = receivers; _i < receivers_3.length; _i++) {
                var connection = receivers_3[_i];
                connection.signal = null;
            }
            scheduleCleanup(receivers);
        }
        var senders = sendersForReceiver.get(obj);
        if (senders != null && senders.length !== 0) {
            for (var _a = 0, senders_3 = senders; _a < senders_3.length; _a++) {
                var connection = senders_3[_a];
                connection.signal = null;
            }
            scheduleCleanup(senders);
        }
    }
    Signal.disconnectAll = disconnectAll;
})(Signal = exports.Signal || (exports.Signal = {}));
exports.Signal = Signal;
function Signalable(Base) {
    // XXX: `class Foo extends Signalable(Object)` doesn't work (compiles, but fails at runtime), so
    // we have to do this to allow signalable classes without an explict base class.
    if (Base != null) {
        return /** @class */ (function (_super) {
            tslib_1.__extends(class_1, _super);
            function class_1() {
                return _super !== null && _super.apply(this, arguments) || this;
            }
            class_1.prototype.connect = function (signal, slot) {
                return signal.connect(slot, this);
            };
            return class_1;
        }(Base));
    }
    else {
        return /** @class */ (function () {
            function class_2() {
            }
            class_2.prototype.connect = function (signal, slot) {
                return signal.connect(slot, this);
            };
            return class_2;
        }());
    }
}
exports.Signalable = Signalable;
var _Signalable;
(function (_Signalable) {
    function connect(signal, slot) {
        return signal.connect(slot, this);
    }
    _Signalable.connect = connect;
})(_Signalable = exports._Signalable || (exports._Signalable = {}));
var receiversForSender = new WeakMap();
var sendersForReceiver = new WeakMap();
function findConnection(conns, signal, slot, context) {
    return array_1.find(conns, function (conn) { return conn.signal === signal && conn.slot === slot && conn.context === context; });
}
var dirtySet = new data_structures_1.Set();
function scheduleCleanup(connections) {
    if (dirtySet.size === 0) {
        callback_1.defer(cleanupDirtySet);
    }
    dirtySet.add(connections);
}
function cleanupDirtySet() {
    dirtySet.forEach(function (connections) {
        array_1.removeBy(connections, function (connection) { return connection.signal == null; });
    });
    dirtySet.clear();
}
