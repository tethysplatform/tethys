
import ReactPlayer from "https://esm.sh/react-player@3.4.0/?deps=react@19.0,react-dom@19.0,react-is@19.0";
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