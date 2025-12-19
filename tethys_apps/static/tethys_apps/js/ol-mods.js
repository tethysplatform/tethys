import Vector from 'https://esm.sh/ol@10.4.0/source/Vector';
import Feature from 'https://esm.sh/ol@10.4.0/Feature';
import * as FormatLib from 'https://esm.sh/ol@10.4.0/format';

export function VectorSource (...props) {
    let format, features;
    props = props[0];
    if (!props.options) props.options = {};
    
    if (props.format || props.options.format) {
        format = props.format || props.options.format;
        if (typeof format === "string") {
            format = new FormatLib[format]();
        }
        if (props.format) {
            props.format = format;
        } else {
            props.options.format = format;
        }
    }
    
    if (props.features || props.options.features) {
        if (!format) {
            throw Error("Format must be specified when features are provided");
        }
        features = props.features || props.options.features;
        if (Array.isArray(features) && features.length > 0 && features[0] instanceof Feature) {
            'pass';
        } else {
            features = format.readFeatures(features);
        }
        if (props.features) {
            props.features = features;
        } else {
            props.options.features = features;
        }
    }
    return React.createElement('source', {cls: Vector, ...props});
}