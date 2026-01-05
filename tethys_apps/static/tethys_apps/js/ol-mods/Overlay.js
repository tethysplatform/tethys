import OLOverlay from 'https://esm.sh/ol@10.7.0/Overlay.js';

const OVERLAYS_DOM_NODE = document.createElement('div');
const OVERLAYS_ROOT = ReactDOM.createRoot(OVERLAYS_DOM_NODE);
const OVERLAYS = {};
document.body.appendChild(OVERLAYS_DOM_NODE);

function renderNode(type, attributes, children) {
    if (Array.isArray(children) && children.length > 0) {
        children = children.map((child) => typeof child === "string" ? child : renderNode(child.tagName, child.attributes, child.children))
    }
    return React.createElement(type, attributes, children)
}

export default function Overlay(...props) {
    props = props[0];

    if (props.element) {
        if (props.element instanceof HTMLElement) {
            "pass";
        } else {
            let Element;
            if (typeof props.element === 'string') {
                Element = document.getElementById(props.element);
            } else if (typeof props.element === "object" && props.element.tagName) {
                Element = document.getElementById(props.element.attributes.id);
                if (!Element) {
                    props.element.attributes.hidden = true;
                }
                OVERLAYS[props.element.attributes.id] = props.element;
                OVERLAYS_ROOT.render(
                    renderNode("div", {}, Object.values(OVERLAYS))
                );
            }
            props.element = Element;
        }
    }
    return React.createElement('overlay', {cls: OLOverlay, ...props});
}