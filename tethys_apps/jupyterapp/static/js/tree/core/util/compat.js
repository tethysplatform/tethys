"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.is_ie = (navigator.userAgent.indexOf('MSIE') >= 0) ||
    (navigator.userAgent.indexOf('Trident') > 0) ||
    (navigator.userAgent.indexOf('Edge') > 0);
exports.is_little_endian = (function () {
    var buf = new ArrayBuffer(4);
    var buf8 = new Uint8Array(buf);
    var buf32 = new Uint32Array(buf);
    buf32[1] = 0x0a0b0c0d;
    var little_endian = true;
    if (buf8[4] == 0x0a && buf8[5] == 0x0b && buf8[6] == 0x0c && buf8[7] == 0x0d) {
        little_endian = false;
    }
    return little_endian;
})();
