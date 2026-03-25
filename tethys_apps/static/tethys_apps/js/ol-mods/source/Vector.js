import _VectorSource from 'https://esm.sh/ol@10.7.0/source/Vector';
import * as FormatLib from 'https://esm.sh/ol@10.7.0/format';
import Feature from 'https://esm.sh/ol@10.7.0/Feature';
import * as GeomLib from 'https://esm.sh/ol@10.7.0/geom';
import Style from 'https://esm.sh/ol@10.7.0/style/Style.js';
import Icon from 'https://esm.sh/ol@10.7.0/style/Icon.js';

export default function VectorSource (...props) {
    let format, features;
    props = props[0];
    if (!props.options) props.options = {};
    
    if (props.format || props.options.format) {
        format = props.format || props.options.format;
        if (typeof format === "string" && format != "olFeature") {
            format = new FormatLib[format]();
        }
        if (props.format) {
            props.format = format;
        } else {
            props.options.format = format;
        }
    }
    
    if (props.features || props.options.features) {
        features = props.features || props.options.features;
        if (Array.isArray(features) && features.length > 0 && features[0] instanceof Feature) {
            'pass';
        } else {
            if (!format) {
                throw Error("Format must be specified when features are provided");
            }
            if (format == "olFeature") {
                features = features.map(function (value) {
                    let style;
                    if (!(value.geometry instanceof GeomLib['Geometry'])) {
                        let geomType = value.geometry.type.split('ol.geom.')[1];
                        value.geometry = new GeomLib[geomType](value.geometry.geom);
                    }
                    if (value.style) {
                        debugger;
                        if (value.style.image && value.style.image.type == "ol.style.Icon") {
                            value.style.image = new Icon(value.style.image)
                        }
                        style = new Style(value.style);
                        delete value.style;
                    }
                    let feature =  new Feature(value);
                    if (style) {
                        feature.setStyle(style);
                    }
                    return feature;
                })
                delete props.format;
                delete props.options.format;
            } else {
                features = format.readFeatures(features);
            }
        }
        if (props.features) {
            props.features = features;
        } else {
            props.options.features = features;
        }
    }
    return React.createElement('source', {cls: _VectorSource, ...props});
}