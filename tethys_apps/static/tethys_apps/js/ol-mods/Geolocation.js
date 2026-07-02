import Geolocation_ from 'ol/Geolocation.js';
import Projection from 'ol/proj/Projection';
import proj4 from 'proj4';
import {register} from 'ol/proj/proj4';

export default function Geolocation(props, context) {
    let [geolocation, setGeolocation] = React.useState(null);
    React.useEffect(() => {
        let _geolocation, projection, onChangeFunc, onErrorFunc;
        if (props.projection) {
            projection = props.projection;
            if (typeof projection === "string" || projection instanceof Projection) {
                "pass";
            } else {
                if (projection.definition) {
                    proj4.defs(projection.code, projection.definition);
                    register(proj4);
                    delete projection.definition;
                }
                projection = new Projection(projection);
            }
        } else {
            projection = new Projection({code: 'EPSG:3857'});
        }
        props.projection = projection;
        if (props.onChange) {
            onChangeFunc = props.onChange;
        }
        if (props.onError) {
            onErrorFunc = props.onError;
        }
        if (geolocation === null) {
            _geolocation = new Geolocation_(JSON.parse(JSON.stringify(props)));  // Removes on* functions
        } else {
            _geolocation = geolocation;
            if (onChangeFunc) {
                _geolocation.un('change', _geolocation.__onChangeFunc);
            }
            if (onErrorFunc) {
                _geolocation.un('error', _geolocation.__onErrorFunc);
            }
        }
        if (onChangeFunc) {
            _geolocation.__onChangeFunc = onChangeFunc;
            _geolocation.on('change', _geolocation.__onChangeFunc);
        }
        if (onErrorFunc) {
            _geolocation.__onErrorFunc = onErrorFunc;
            _geolocation.on('error', function (e) {
                window.setTimeout(function () {
                    _geolocation.__onErrorFunc(e);
                }, 2000);
            });
        }
        if (geolocation === null) {
            setGeolocation(_geolocation);
        }
    }, [props.onChange, props.onError]);
    return React.createElement("div", {id: "geolocation-placeholder"});
};