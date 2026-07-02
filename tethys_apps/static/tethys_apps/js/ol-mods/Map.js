import _Map from "@planet/maps/Map.js"
import Group from "@planet/maps/layer/Group.js"

let HIT_FEATURE;

export default function Map (...props) {
    props = props[0];
    let events = findVectorLayerEvents(props, ["onClick", "onPointerFeatureChange"]);
    for (const [layerId, eventInfo] of Object.entries(events)) {
        if (eventInfo.type == "onClick") {
            props.onClick = ((wrappedLayerId, wrappedEventFunc) => function (evt) {
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
            })(layerId, eventInfo.handler);
        } else if (eventInfo.type == "onPointerFeatureChange") {
            if (eventInfo.handler.__applied) {
            }
            props.onPointerMove = ((wrappedLayerId, wrappedEventFunc, timer) => function (evt) {
                clearTimeout(timer);
                timer = setTimeout(() => {
                    let newHitFeature = undefined;
                    let featureData = {"feature": null};
                    let layer = getLayerById(evt.map, wrappedLayerId);
                    if (layer) {
                        layer.getFeatures(evt.pixel).then(function (features) {
                            const feature = features.length ? features[0] : undefined;
                            if (feature && feature !== HIT_FEATURE) {
                                featureData.feature = feature.getProperties();
                                newHitFeature = feature;
                            }
                            if (HIT_FEATURE !== newHitFeature) {
                                HIT_FEATURE = newHitFeature;
                                return wrappedEventFunc(featureData);
                            }
                        });
                    }
                }, 500);
            })(layerId, eventInfo.handler);
            props.onPointerMove.__applied = true;
        }
    }
    return _Map(props)
}

const randomId = function(length = 6) {
    return Math.random().toString(36).substring(2, length + 2);
};

const getLayerById = function (map, id) {
    return map.getAllLayers().find(layer => layer.get("layerId")  === id);
}

function findVectorLayerEvents(obj, eventProps) {
    let events = {};
    let children = obj.children;
    if (!Array.isArray(children)) {
        children = [children];
    }
    for (const child of children) {
        if (child.type === Group) {
            if (child.props.options.title === "Basemap") continue;
            if (child.props.children) {
                events = {...events, ...findVectorLayerEvents(child.props, eventProps)}
            }
        } else if (child.type.name === "VectorLayer") {
            eventProps.forEach(function (eventProp) {
                if (child.props.hasOwnProperty(eventProp)) {
                    if (!child.props.hasOwnProperty("options")) {
                        child.props.properties = {};
                    }
                    child.props.properties.layerId = randomId();
                    events[child.props.properties.layerId] = {
                        "type": eventProp,
                        "handler": child.props[eventProp]
                    }
                }
            })
        }
    }
    return events;
}