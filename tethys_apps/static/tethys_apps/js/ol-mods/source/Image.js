import _ImageSource from 'https://esm.sh/ol@10.7.0/source/Image';
import {load} from 'https://esm.sh/ol@10.7.0/Image';
import {createLoader} from 'https://esm.sh/ol@10.7.0/source/wms';

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
    return React.createElement('source', {cls: _ImageSource, ...props});
}