import _ImageSource from 'planet_maps/source/Image';
import {load} from 'ol/Image';
import {createLoader} from 'ol/source/wms';

export default function ImageSource (...props) {
    let loader;
    props = props[0];
    if (!props.options) props.options = {};
    
    if (props.loader || props.options.loader) {
        loader = props.loader || props.options.loader;
        if (typeof loader === "object") {
            if (loader.load) {
                loader.load = load
            }
            loader = createLoader(loader);
        }
        if (props.loader) {
            props.loader = loader;
        } else {
            props.options.loader = loader;
        }
    }
    return _ImageSource(props);
}