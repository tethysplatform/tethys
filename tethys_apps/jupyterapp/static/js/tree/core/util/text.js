"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var dom_1 = require("../dom");
var cache = {};
function get_text_height(font) {
    if (cache[font] != null)
        return cache[font];
    var text = dom_1.span({ style: { font: font } }, "Hg");
    var block = dom_1.div({ style: { display: "inline-block", width: "1px", height: "0px" } });
    var elem = dom_1.div({}, text, block);
    document.body.appendChild(elem);
    try {
        block.style.verticalAlign = "baseline";
        var ascent = dom_1.offset(block).top - dom_1.offset(text).top;
        block.style.verticalAlign = "bottom";
        var height = dom_1.offset(block).top - dom_1.offset(text).top;
        var result = { height: height, ascent: ascent, descent: height - ascent };
        cache[font] = result;
        return result;
    }
    finally {
        document.body.removeChild(elem);
    }
}
exports.get_text_height = get_text_height;
