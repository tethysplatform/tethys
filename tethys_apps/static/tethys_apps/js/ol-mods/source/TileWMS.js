import _TileWMSSource from '@planet/maps/source/TileWMS';
import TileGrid from 'ol/tilegrid/TileGrid';

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
    return _TileWMSSource(props);
}