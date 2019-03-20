"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var signaling_1 = require("./signaling");
exports.clear_menus = new signaling_1.Signal0({}, "clear_menus");
document.addEventListener("click", function () { return exports.clear_menus.emit(); });
