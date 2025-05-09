
import {Col, Row, Container} from "https://esm.sh/react-bootstrap/?deps=react@19.0,react-dom@19.0,react-is@19.0&exports=Col,Row,Container";
export {Col, Row, Container};
loadCSS("https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css");
import ImageLayer from "https://esm.sh/@planet/maps@11.2.0/layer/Image?deps=react@19.0,react-dom@19.0,react-is@19.0,ol@10.4.0";
import ImageArcGISRest from "https://esm.sh/@planet/maps@11.2.0/source/ImageArcGISRest?deps=react@19.0,react-dom@19.0,react-is@19.0,ol@10.4.0";
import Map from "https://esm.sh/@planet/maps@11.2.0/Map?deps=react@19.0,react-dom@19.0,react-is@19.0,ol@10.4.0";
import View from "https://esm.sh/@planet/maps@11.2.0/View?deps=react@19.0,react-dom@19.0,react-is@19.0,ol@10.4.0";
import XYZ from "https://esm.sh/@planet/maps@11.2.0/source/XYZ?deps=react@19.0,react-dom@19.0,react-is@19.0,ol@10.4.0";
import OSM from "https://esm.sh/@planet/maps@11.2.0/source/OSM?deps=react@19.0,react-dom@19.0,react-is@19.0,ol@10.4.0";
import LayerGroup from "https://esm.sh/@planet/maps@11.2.0/layer/Group?deps=react@19.0,react-dom@19.0,react-is@19.0,ol@10.4.0";
import VectorLayer from "https://esm.sh/@planet/maps@11.2.0/layer/Tile?deps=react@19.0,react-dom@19.0,react-is@19.0,ol@10.4.0";
import ScaleLine from "https://esm.sh/@planet/maps@11.2.0/control/ScaleLine?deps=react@19.0,react-dom@19.0,react-is@19.0,ol@10.4.0";
export {ImageLayer, ImageArcGISRest, Map, View, XYZ, OSM, LayerGroup, VectorLayer, ScaleLine};
loadCSS("https://esm.sh/ol@10.4.0/ol.css");
import {LayerPanel} from "/static/tethys_apps/js/layer-panel.js/?deps=react@19.0,react-dom@19.0,react-is@19.0&exports=LayerPanel";
export {LayerPanel};
loadCSS("https://esm.sh/ol-layerswitcher@4.1.2/dist/ol-layerswitcher.css");
loadCSS("https://esm.sh/ol-side-panel@1.0.6/src/SidePanel.css");
import {LineChart, CartesianGrid, XAxis, YAxis, Tooltip, Line} from "https://esm.sh/recharts/?deps=react@19.0,react-dom@19.0,react-is@19.0&exports=LineChart,CartesianGrid,XAxis,YAxis,Tooltip,Line";
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

function stringifyToDepth(val, depth, replacer, space) {
    depth = isNaN(+depth) ? 1 : depth;
    function _build(key, val, depth, o, a) { // (JSON.stringify() has it's own rules, which we respect here by using it for property iteration)
        return !val || typeof val != 'object' ? val : (a=Array.isArray(val), JSON.stringify(val, function(k,v){ if (a || depth > 0) { if (replacer) v=replacer(k,v); if (!k) return (a=Array.isArray(v),val=v); !o && (o=a?[]:{}); o[k] = _build(k, v, a?depth:depth-1); } }), o||(a?[]:{}));
    }
    return JSON.stringify(_build('', val, depth), null, space);
}

function stringifyReplacer (key, value) {
    if (key === '') return value;
    try {
        JSON.stringify(value);
        return value;
    } catch (err) {
        return (typeof value === 'object') ? value : undefined;
    }
}

function makeJsonSafeEventHandler(oldHandler) {
    // Since we can't really know what the event handlers get passed we have to check if
    // they are JSON serializable or not. We can allow normal synthetic events to pass
    // through since the original handler already knows how to serialize those for us.
    return function safeEventHandler() {

        var filteredArguments = [];
        Array.from(arguments).forEach(function (arg) {
            let filteredArg = arg;
            if (typeof arg === "object") {
                if (arg.nativeEvent) {
                    // this is probably a standard React synthetic event
                    filteredArg = arg;
                } else {
                    filteredArg = JSON.parse(stringifyToDepth(arg, 3, stringifyReplacer));
                }
                
                if (arg.__proto__) {
                    Object.getOwnPropertyNames(arg.__proto__).forEach(function (propName) {
                        if (propName == 'constructor') return;
                        if (!arg.hasOwnProperty(propName) && arg[propName]) {
                            filteredArg[propName] = arg[propName];
                            delete filteredArg[propName + '_'];
                        }
                    });
                }
            }
            // Add non-enumerable properties 
            filteredArguments.push(filteredArg);
        });
        oldHandler(...Array.from(filteredArguments));
    };
}