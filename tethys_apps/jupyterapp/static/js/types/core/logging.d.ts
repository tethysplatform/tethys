export declare class LogLevel {
    readonly name: string;
    readonly level: number;
    constructor(name: string, level: number);
}
export declare class Logger {
    static TRACE: LogLevel;
    static DEBUG: LogLevel;
    static INFO: LogLevel;
    static WARN: LogLevel;
    static ERROR: LogLevel;
    static FATAL: LogLevel;
    static OFF: LogLevel;
    static log_levels: {
        [key: string]: LogLevel;
    };
    static readonly levels: string[];
    static get(name: string, level?: LogLevel): Logger;
    _name: string;
    _log_level: LogLevel;
    constructor(name: string, level?: LogLevel);
    readonly level: LogLevel;
    get_level(): LogLevel;
    set_level(log_level: LogLevel | string): void;
    trace(..._args: any[]): void;
    debug(..._args: any[]): void;
    info(..._args: any[]): void;
    warn(..._args: any[]): void;
    error(..._args: any[]): void;
}
export declare const logger: Logger;
export declare function set_log_level(level: string): void;
