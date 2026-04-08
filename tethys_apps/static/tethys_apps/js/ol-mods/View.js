import _View from "@planet/maps/View.js?external=react,react-dom,ol"
import Projection from 'ol/proj/Projection';
import proj4 from 'proj4';
import {register} from 'ol/proj/proj4';

export default function View (...props) {
    let projection;
    props = props[0];
    if (!props.options) props.options = {};
    
    if (props.options.projection) {
        projection = props.options.projection;
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
        props.options.projection = projection;
    }
    return _View(props);
}