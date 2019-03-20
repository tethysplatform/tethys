"use strict";
// TODO Clear out debugging code, etc.
// TODO Organize helper functions.
// TODO The years ticker doesn't always use the roundest numbers; it should
// probably use a special ticker.
// TODO Add tests.
// TODO There used to be a TODO: restore memoization.  So.... do that?
// TODO Instead of a get_ticks() method, there used to be an auto_ticks()
// function that took a lot of fancy arguments, but those arguments weren't
// used anywhere.  Should we restore them?
Object.defineProperty(exports, "__esModule", { value: true });
// Some time constants, in milliseconds.
exports.ONE_MILLI = 1.0;
exports.ONE_SECOND = 1000.0;
exports.ONE_MINUTE = 60.0 * exports.ONE_SECOND;
exports.ONE_HOUR = 60 * exports.ONE_MINUTE;
exports.ONE_DAY = 24 * exports.ONE_HOUR;
exports.ONE_MONTH = 30 * exports.ONE_DAY; // An approximation, obviously.
exports.ONE_YEAR = 365 * exports.ONE_DAY;
// ---------------------------------------------------------------------------
// Date/time utility functions
// ---------------------------------------------------------------------------
// Makes a copy of a date object.
function copy_date(date) {
    return new Date(date.getTime());
}
exports.copy_date = copy_date;
// Rounds a date down to the month.
function last_month_no_later_than(date) {
    var new_date = copy_date(date);
    new_date.setUTCDate(1);
    new_date.setUTCHours(0);
    new_date.setUTCMinutes(0);
    new_date.setUTCSeconds(0);
    new_date.setUTCMilliseconds(0);
    return new_date;
}
exports.last_month_no_later_than = last_month_no_later_than;
// Rounds a date down to the year.
function last_year_no_later_than(date) {
    var new_date = last_month_no_later_than(date);
    new_date.setUTCMonth(0);
    return new_date;
}
exports.last_year_no_later_than = last_year_no_later_than;
