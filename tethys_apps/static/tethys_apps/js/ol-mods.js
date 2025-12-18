import Vector from 'https://esm.sh/ol@10.4.0/source/Vector';
import * as FormatLib from 'https://esm.sh/ol@10.4.0/format';

export function VectorSource (...props) {
    if (props[0].options.format && typeof props[0].options.format === "string" ) {
        props[0].options.format = new FormatLib[props[0].options.format]()
    }
    props = props[0];
    return React.createElement('source', {cls: Vector, ...props});
}