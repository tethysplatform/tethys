import _VectorLayer from 'https://esm.sh/ol@10.7.0/layer/Vector';
import * as StyleLib from 'https://esm.sh/ol@10.7.0/style';

export default function VectorLayer (...props) {
    let style;
    props = props[0];
    if (!props.options) props.options = {};

    if (props.style || props.options.style) {
        style = props.style || props.options.style;
        if (style instanceof StyleLib["Style"] || typeof style === "function") {
            "pass";
        } else {
            if (typeof style === "object" && style.method === "unique_values" && style.hasOwnProperty("fields") && style.hasOwnProperty("values")) {
                style = ((wrappedStyle) => (feature, resolution) => _uniqueValuesStyler(wrappedStyle, feature, resolution))(style)
            } else {
                style = ((wrappedStyle) => (feature, resolution) => _bottomUpClone(wrappedStyle, feature, resolution, _createStyleObject))(style)
            }
        }
        if (props.style) {
            props.style = style;
        } else {
            props.options.style = style;
        }
    }
    
    return React.createElement('layer', {cls: _VectorLayer, ...props});
}

const _uniqueValuesStyler = (styleObj, feature, resolution) => {
    let style = styleObj.default;
    let key = '';
    styleObj.fields.forEach(function (field) {
        key += feature.get(field);
        key += "__";
    });
    key = key.slice(0, -2);
    for (const styleDef of styleObj.values) {
        if (styleDef.slice(0, -1).join('') == key) {
            style = styleDef.slice(-1)[0];
        }
    }
    style = _bottomUpClone(style, feature, resolution, _createStyleObject);
    return style;
};

const _createStyleObject = (key, value, feature, resolution) => {
  if (typeof value === "string" && value.includes("%{")) {
    const regex = /%\{\s*\$feature\.(\w+)\s*\}/g;
    const matchesIterator = value.matchAll(regex);
    const attributes = Array.from(matchesIterator, match => match[1].trim());
    let newValue = value;
    attributes.forEach(function (attr) {
        let replaceRegex = new RegExp(`%{\\s*\\$feature\\.${attr}\\s*}`, 'gi');
        newValue = newValue.replace(replaceRegex, feature.get(attr));
    });
    value = newValue;
  } else if (typeof value === 'object' && value.type && typeof value.type == "string" && value.type.includes("ol.style")) {
    let styleClass = StyleLib[value.type.split('ol.style.')[1]];
    delete value.type;
    return new styleClass(value);
  }
  return value;
};

/**
 * Recursively traverses an object from bottom-up (post-order) 
 * and recreates it, applying an optional transformation callback.
 * 
 * @param {object | array} input - The object or array to traverse.
 * @param {function} [callback] - An optional function (key, value, feature, resolution) => transformedValue.
 * @returns {object | array} A new, transformed object or array.
 */
function _bottomUpClone(input, feature, resolution, callback = (k, v) => v) {
  // 1. Base case: handle primitives, null, and non-object types.
  if (input === null || typeof input !== 'object') {
    return callback(null, input, feature, resolution);
  }

  // 2. Handle Arrays: recursively process each element.
  if (Array.isArray(input)) {
    const newArray = input.map(item => _bottomUpClone(item, feature, resolution, callback));
    // Apply callback to the array itself after its children are processed
    return callback(null, newArray, feature, resolution);
  }

  // 3. Handle Objects: recursively process each property.
  const newObject = {};
  for (const key in input) {
    if (Object.hasOwnProperty.call(input, key)) {
      // The magic happens here: the value assigned is the result 
      // of the recursive call on the child, ensuring bottom-up processing.
      newObject[key] = _bottomUpClone(input[key], feature, resolution, callback);
    }
  }

  // 4. Apply callback to the current object after its children are processed.
  return callback(null, newObject, feature, resolution);
}