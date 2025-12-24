import _View from 'https://esm.sh/ol@10.7.0/View';
import Projection from 'https://esm.sh/ol@10.7.0/proj/Projection';
import proj4 from 'https://esm.sh/proj4?deps=ol@10.7.0';
import {register} from 'https://esm.sh/ol@10.7.0/proj/proj4';

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
    return React.createElement('view', {cls: _View, ...props});
}