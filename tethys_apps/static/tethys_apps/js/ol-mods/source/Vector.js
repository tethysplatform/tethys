import _VectorSource from 'https://esm.sh/ol@10.7.0/source/Vector';
import * as FormatLib from 'https://esm.sh/ol@10.7.0/format';
import Feature from 'https://esm.sh/ol@10.7.0/Feature';

export default function VectorSource (...props) {
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
    return React.createElement('source', {cls: _VectorSource, ...props});
}