
import {Col, Row, Container} from "https://esm.sh/react-bootstrap@2.10.10/?deps=react@19.0,react-dom@19.0,react-is@19.0&exports=Col,Row,Container";
export {Col, Row, Container};
loadCSS("https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css");
import ImageLayer from "https://esm.sh/@planet/maps@11.2.0/layer/Image.js?deps=react@19.0,react-dom@19.0,react-is@19.0,ol@10.7.0";
import ImageArcGISRestSource from "https://esm.sh/@planet/maps@11.2.0/source/ImageArcGISRest.js?deps=react@19.0,react-dom@19.0,react-is@19.0,ol@10.7.0";
import XYZSource from "https://esm.sh/@planet/maps@11.2.0/source/XYZ.js?deps=react@19.0,react-dom@19.0,react-is@19.0,ol@10.7.0";
import OSMSource from "https://esm.sh/@planet/maps@11.2.0/source/OSM.js?deps=react@19.0,react-dom@19.0,react-is@19.0,ol@10.7.0";
import GroupLayer from "https://esm.sh/@planet/maps@11.2.0/layer/Group.js?deps=react@19.0,react-dom@19.0,react-is@19.0,ol@10.7.0";
import TileLayer from "https://esm.sh/@planet/maps@11.2.0/layer/Tile.js?deps=react@19.0,react-dom@19.0,react-is@19.0,ol@10.7.0";
import ScaleLineControl from "https://esm.sh/@planet/maps@11.2.0/control/ScaleLine.js?deps=react@19.0,react-dom@19.0,react-is@19.0,ol@10.7.0";
export {ImageLayer, ImageArcGISRestSource, XYZSource, OSMSource, GroupLayer, TileLayer, ScaleLineControl};
loadCSS("https://esm.sh/ol@10.7.0/ol.css");
import {LayerPanel} from "/static/tethys_apps/js/layer-panel.js/?deps=react@19.0,react-dom@19.0,react-is@19.0&exports=LayerPanel";
export {LayerPanel};
loadCSS("https://esm.sh/ol-layerswitcher@4.1.2/dist/ol-layerswitcher.css");
loadCSS("https://esm.sh/ol-side-panel@1.0.6/src/SidePanel.css");
import VectorSource from "/static/tethys_apps/js/ol-mods/source/Vector.js?deps=react@19.0,react-dom@19.0,react-is@19.0";
import VectorLayer from "/static/tethys_apps/js/ol-mods/layer/Vector.js?deps=react@19.0,react-dom@19.0,react-is@19.0";
import Map from "/static/tethys_apps/js/ol-mods/Map.js?deps=react@19.0,react-dom@19.0,react-is@19.0";
import View from "/static/tethys_apps/js/ol-mods/View.js?deps=react@19.0,react-dom@19.0,react-is@19.0";
export {VectorSource, VectorLayer, Map, View};
import {LineChart, CartesianGrid, XAxis, YAxis, Tooltip, Line} from "https://esm.sh/recharts@2.12.7/?deps=react@19.0,react-dom@19.0,react-is@19.0&exports=LineChart,CartesianGrid,XAxis,YAxis,Tooltip,Line";
export {LineChart, CartesianGrid, XAxis, YAxis, Tooltip, Line};

function loadCSS(href) {  
    var head = document.getElementsByTagName('head')[0];

    if (document.querySelectorAll(`link[href="${href}"]`).length === 0) {
        // Creating link element 
        var style = document.createElement('link');
        style.id = href;
        style.href = href;
        style.type = 'text/css';
        style.rel = 'stylesheet';
        head.append(style);
    }
}


export function bind(node, config) {
    const root = ReactDOM.createRoot(node);
    return {
        create: (component, props, children) =>
            React.createElement(component, wrapEventHandlers(props), ...children),
        render: (element) => root.render(element),
        unmount: () => root.unmount()
    };
}


function wrapEventHandlers(props) {
    const newProps = Object.assign({}, props);
    for (const [key, value] of Object.entries(props)) {
        if (typeof value === "function") {
            newProps[key] = makeJsonSafeEventHandler(value);
        }
    }
    return newProps;
}

/**
 * Converts an HTML element and its children into a structured JavaScript object.
 * @param {HTMLElement} element The HTML element to convert.
 * @return {object} The structured object.
 */
function htmlToJsonObject(element) {
  if (!element) return null;

  const obj = {
    tagName: element.tagName.toLowerCase(),
    attributes: {}
  };

  // Get attributes
  for (let i = 0; i < element.attributes.length; i++) {
    const attr = element.attributes[i];
    obj.attributes[attr.name] = attr.value;
  }

  return obj;
}

function jsonSanitizeObject(obj, maxDepth, refs, depth) {
    try {
        JSON.stringify(obj);
        return obj;
    } catch (e) {
        "pass";
    }
    if (!maxDepth) {
        maxDepth = 4;
    }
    if (!depth) {
        depth = 0;
    }
    if (!refs) {
        refs = [];
    }
    if (typeof obj === 'string' || typeof obj === 'number' || obj == null || typeof obj === 'boolean') {
        return obj;
    }
    if (typeof obj === 'function') {
        return undefined;
    }
    if (obj.constructor === Window) {
        return undefined;
    }
    if (refs.includes(obj)) {
        return undefined;
    }
    refs.push(obj);
    let newObj = Array.isArray(obj) ? [] : {};
    if (depth > maxDepth) {
        newObj = "BEYOND MAX DEPTH";
    } else {
        for (const [key, value] of Object.entries(obj)) {
            if (refs.includes(value)) continue;
            newObj[key] = jsonSanitizeObject(value, maxDepth, refs, depth+1);
        }
        if (obj.__proto__) {
            Object.getOwnPropertyNames(obj.__proto__).forEach(function (propName) {
                newObj[propName] = jsonSanitizeObject(obj[propName], maxDepth, refs, depth+1);
            });
        }
        if (obj instanceof Element) {
            newObj = {...newObj, ...htmlToJsonObject(obj)}
        }
    }
    return newObj;
}

function makeJsonSafeEventHandler(oldHandler) {
    // Since we can't really know what the event handlers get passed we have to check if
    // they are JSON serializable or not. We can allow normal synthetic events to pass
    // through since the original handler already knows how to serialize those for us.
    return function safeEventHandler() {
        oldHandler(...Array.from(arguments).map((x) => jsonSanitizeObject(x, 4)));
    };
}