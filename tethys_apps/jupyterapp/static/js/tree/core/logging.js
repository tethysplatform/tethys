"use strict";
// This is based on https://github.com/pimterry/loglevel
Object.defineProperty(exports, "__esModule", { value: true });
var types_1 = require("./util/types");
var _loggers = {};
var LogLevel = /** @class */ (function () {
    function LogLevel(name, level) {
        this.name = name;
        this.level = level;
    }
    return LogLevel;
}());
exports.LogLevel = LogLevel;
var Logger = /** @class */ (function () {
    function Logger(name, level) {
        if (level === void 0) { level = Logger.INFO; }
        this._name = name;
        this.set_level(level);
    }
    Object.defineProperty(Logger, "levels", {
        get: function () {
            return Object.keys(Logger.log_levels);
        },
        enumerable: true,
        configurable: true
    });
    Logger.get = function (name, level) {
        if (level === void 0) { level = Logger.INFO; }
        if (name.length > 0) {
            var logger_1 = _loggers[name];
            if (logger_1 == null)
                _loggers[name] = logger_1 = new Logger(name, level);
            return logger_1;
        }
        else
            throw new TypeError("Logger.get() expects a non-empty string name and an optional log-level");
    };
    Object.defineProperty(Logger.prototype, "level", {
        get: function () {
            return this.get_level();
        },
        enumerable: true,
        configurable: true
    });
    Logger.prototype.get_level = function () {
        return this._log_level;
    };
    Logger.prototype.set_level = function (log_level) {
        if (log_level instanceof LogLevel)
            this._log_level = log_level;
        else if (types_1.isString(log_level) && Logger.log_levels[log_level] != null)
            this._log_level = Logger.log_levels[log_level];
        else
            throw new Error("Logger.set_level() expects a log-level object or a string name of a log-level");
        var logger_name = "[" + this._name + "]";
        for (var name_1 in Logger.log_levels) {
            var log_level_1 = Logger.log_levels[name_1];
            if (log_level_1.level < this._log_level.level || this._log_level.level === Logger.OFF.level)
                this[name_1] = function () { };
            else
                this[name_1] = _method_factory(name_1, logger_name);
        }
    };
    Logger.prototype.trace = function () {
        var _args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _args[_i] = arguments[_i];
        }
    };
    Logger.prototype.debug = function () {
        var _args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _args[_i] = arguments[_i];
        }
    };
    Logger.prototype.info = function () {
        var _args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _args[_i] = arguments[_i];
        }
    };
    Logger.prototype.warn = function () {
        var _args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _args[_i] = arguments[_i];
        }
    };
    Logger.prototype.error = function () {
        var _args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _args[_i] = arguments[_i];
        }
    };
    Logger.TRACE = new LogLevel("trace", 0);
    Logger.DEBUG = new LogLevel("debug", 1);
    Logger.INFO = new LogLevel("info", 2);
    Logger.WARN = new LogLevel("warn", 6);
    Logger.ERROR = new LogLevel("error", 7);
    Logger.FATAL = new LogLevel("fatal", 8);
    Logger.OFF = new LogLevel("off", 9);
    Logger.log_levels = {
        trace: Logger.TRACE,
        debug: Logger.DEBUG,
        info: Logger.INFO,
        warn: Logger.WARN,
        error: Logger.ERROR,
        fatal: Logger.FATAL,
        off: Logger.OFF,
    };
    return Logger;
}());
exports.Logger = Logger;
function _method_factory(method_name, logger_name) {
    if (console[method_name] != null)
        return console[method_name].bind(console, logger_name);
    else if (console.log != null)
        return console.log.bind(console, logger_name);
    else
        return function () { };
}
exports.logger = Logger.get("bokeh");
function set_log_level(level) {
    if (Logger.log_levels[level] == null) {
        console.log("[bokeh] unrecognized logging level '" + level + "' passed to Bokeh.set_log_level(), ignoring");
        console.log("[bokeh] valid log levels are: " + Logger.levels.join(', '));
    }
    else {
        console.log("[bokeh] setting log level to: '" + level + "'");
        exports.logger.set_level(level);
    }
}
exports.set_log_level = set_log_level;
