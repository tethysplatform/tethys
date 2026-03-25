import _Map from "https://esm.sh/@planet/maps@11.2.0/Map.js?deps=react@19.0,react-dom@19.0,react-is@19.0,ol@10.7.0"
import Group from "https://esm.sh/@planet/maps@11.2.0/layer/Group.js?deps=react@19.0,react-dom@19.0,react-is@19.0,ol@10.7.0"
import VectorLayer from "/static/tethys_apps/js/ol-mods/layer/Vector.js?deps=react@19.0,react-dom@19.0,react-is@19.0"

export default function Map (...props) {
    props = props[0];
    let events = findVectorLayerClickEvents(props, "onClick");
    for (const [layerId, eventFunc] of Object.entries(events)) {
        props["onClick"] = ((wrappedLayerId, wrappedEventFunc) => function (evt) {
            let featureData = {"features": []};
            let layer = getLayerById(evt.map, wrappedLayerId);
            if (layer) {
                layer.getFeatures(evt.pixel).then(function (features) {
                    const feature = features.length ? features[0] : undefined;
                    if (feature) {
                        featureData.features.push(feature.getProperties());
                    }
                    return wrappedEventFunc(featureData);
                });
            }
        })(layerId, eventFunc);
    }
    return _Map(props)
}

const randomId = function(length = 6) {
    return Math.random().toString(36).substring(2, length + 2);
};

const getLayerById = function (map, id) {
    return map.getAllLayers().find(layer => layer.get("layerId")  === id);
}

function findVectorLayerClickEvents(obj) {
    let events = {};
    let children = obj.children;
    if (!Array.isArray(children)) {
        children = [children];
    }
    for (const child of children) {
        if (child.type === Group) {
            if (child.props.options.title === "Basemap") continue;
            if (child.props.children) {
                events = {...events, ...findVectorLayerClickEvents(child.props)}
            }
        } else if (child.type === VectorLayer) {
            if (child.props.onClick) {
                if (!child.props.hasOwnProperty("options")) {
                    child.props.properties = {};
                }
                child.props.properties.layerId = randomId();
                events[child.props.properties.layerId] = child.props.onClick;
            }
        }
    }
    return events;
}