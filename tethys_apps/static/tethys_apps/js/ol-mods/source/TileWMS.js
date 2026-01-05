import _TileWMSSource from 'https://esm.sh/ol@10.7.0/source/TileWMS';
import TileGrid from 'https://esm.sh/ol@10.7.0/tilegrid/TileGrid.js';

export default function TileWMSSource (...props) {
    let tileGrid;
    props = props[0];
    if (!props.options) props.options = {};
    
    if (props.options.tileGrid) {
        tileGrid = props.options.tileGrid;
        if (!(tileGrid instanceof TileGrid)) {
            tileGrid = new TileGrid(tileGrid);
        }
        props.options.tileGrid = tileGrid;
    }
    return React.createElement('source', {cls: _TileWMSSource, ...props});
}