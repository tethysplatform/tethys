import { JSDOM } from "jsdom";


const dom = new JSDOM("<!DOCTYPE html><html><body></body></html>", {
    url: "http://localhost",
});

global.window = dom.window;
global.document = dom.window.document;

const $ = require("jquery");

global.$ = $;
global.jQuery = $;

global.$.fn = global.$.fn || {};