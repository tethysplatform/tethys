
import ReactPlayer from "https://esm.sh/react-player/?deps=react@19.0,react-dom@19.0,react-is@19.0";
export {ReactPlayer};

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
            let filteredArg;
            if (typeof arg === "object" && arg.nativeEvent) {
                // this is probably a standard React synthetic event
                filteredArg = arg;
            } else {
                filteredArg = JSON.parse(stringifyToDepth(arg, 3, stringifyReplacer));
            }
            // Add non-enumerable properties 
            if (arg.__proto__) {
                Object.getOwnPropertyNames(arg.__proto__).forEach(function (propName) {
                    if (propName == 'constructor') return;
                    if (!arg.hasOwnProperty(propName) && arg[propName]) {
                        filteredArg[propName] = arg[propName];
                        delete filteredArg[propName + '_'];
                    }
                });
            }
            filteredArguments.push(filteredArg);
        });
        oldHandler(...Array.from(filteredArguments));
    };
}