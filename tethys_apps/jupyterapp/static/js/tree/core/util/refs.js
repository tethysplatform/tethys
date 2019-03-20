"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var types_1 = require("./types");
// Create a Bokeh reference from a HasProps subclass
//
// @param obj [HasProps] the object to create a reference for
// @return [Object] a Bokeh reference for `obj`
// @throw Error if `obj` is not a HasProps
//
function create_ref(obj) {
    var ref = {
        type: obj.type,
        id: obj.id,
    };
    if (obj._subtype != null) {
        ref.subtype = obj._subtype;
    }
    return ref;
}
exports.create_ref = create_ref;
// Determine whether an object has the proper format of a Bokeh reference
//
// @param arg [Object] the object to test
// @return [bool] whether the object is a refererence
//
// @note this function does not check that the id and types are valid,
//   only that the format is correct (all required keys are present)
//
function is_ref(arg) {
    if (types_1.isObject(arg)) {
        var keys = Object.keys(arg).sort();
        if (keys.length == 2)
            return keys[0] == 'id' && keys[1] == 'type';
        if (keys.length == 3)
            return keys[0] == 'id' && keys[1] == 'subtype' && keys[2] == 'type';
    }
    return false;
}
exports.is_ref = is_ref;
