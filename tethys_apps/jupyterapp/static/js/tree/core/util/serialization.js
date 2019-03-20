"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var types_1 = require("./types");
var compat_1 = require("./compat");
exports.ARRAY_TYPES = {
    uint8: Uint8Array,
    int8: Int8Array,
    uint16: Uint16Array,
    int16: Int16Array,
    uint32: Uint32Array,
    int32: Int32Array,
    float32: Float32Array,
    float64: Float64Array,
};
exports.DTYPES = {
    Uint8Array: "uint8",
    Int8Array: "int8",
    Uint16Array: "uint16",
    Int16Array: "int16",
    Uint32Array: "uint32",
    Int32Array: "int32",
    Float32Array: "float32",
    Float64Array: "float64",
};
function arrayName(array) {
    if ("name" in array.constructor)
        return array.constructor.name;
    else {
        switch (true) {
            case array instanceof Uint8Array: return "Uint8Array";
            case array instanceof Int8Array: return "Int8Array";
            case array instanceof Uint16Array: return "Uint16Array";
            case array instanceof Int16Array: return "Int16Array";
            case array instanceof Uint32Array: return "Uint32Array";
            case array instanceof Int32Array: return "Int32Array";
            case array instanceof Float32Array: return "Float32Array";
            case array instanceof Float64Array: return "Float64Array";
            default:
                throw new Error("unsupported typed array");
        }
    }
}
exports.BYTE_ORDER = compat_1.is_little_endian ? "little" : "big";
function swap16(a) {
    var x = new Uint8Array(a.buffer, a.byteOffset, a.length * 2);
    for (var i = 0, end = x.length; i < end; i += 2) {
        var t = x[i];
        x[i] = x[i + 1];
        x[i + 1] = t;
    }
}
exports.swap16 = swap16;
function swap32(a) {
    var x = new Uint8Array(a.buffer, a.byteOffset, a.length * 4);
    for (var i = 0, end = x.length; i < end; i += 4) {
        var t = x[i];
        x[i] = x[i + 3];
        x[i + 3] = t;
        t = x[i + 1];
        x[i + 1] = x[i + 2];
        x[i + 2] = t;
    }
}
exports.swap32 = swap32;
function swap64(a) {
    var x = new Uint8Array(a.buffer, a.byteOffset, a.length * 8);
    for (var i = 0, end = x.length; i < end; i += 8) {
        var t = x[i];
        x[i] = x[i + 7];
        x[i + 7] = t;
        t = x[i + 1];
        x[i + 1] = x[i + 6];
        x[i + 6] = t;
        t = x[i + 2];
        x[i + 2] = x[i + 5];
        x[i + 5] = t;
        t = x[i + 3];
        x[i + 3] = x[i + 4];
        x[i + 4] = t;
    }
}
exports.swap64 = swap64;
function process_buffer(spec, buffers) {
    var need_swap = spec.order !== exports.BYTE_ORDER;
    var shape = spec.shape;
    var bytes = null;
    for (var _i = 0, buffers_1 = buffers; _i < buffers_1.length; _i++) {
        var buf = buffers_1[_i];
        var header = JSON.parse(buf[0]);
        if (header.id === spec.__buffer__) {
            bytes = buf[1];
            break;
        }
    }
    var arr = new (exports.ARRAY_TYPES[spec.dtype])(bytes);
    if (need_swap) {
        if (arr.BYTES_PER_ELEMENT === 2) {
            swap16(arr);
        }
        else if (arr.BYTES_PER_ELEMENT === 4) {
            swap32(arr);
        }
        else if (arr.BYTES_PER_ELEMENT === 8) {
            swap64(arr);
        }
    }
    return [arr, shape];
}
exports.process_buffer = process_buffer;
function process_array(obj, buffers) {
    if (types_1.isObject(obj) && '__ndarray__' in obj)
        return decode_base64(obj);
    else if (types_1.isObject(obj) && '__buffer__' in obj)
        return process_buffer(obj, buffers);
    else if (types_1.isArray(obj) || types_1.isTypedArray(obj))
        return [obj, []];
    else
        return undefined;
}
exports.process_array = process_array;
function arrayBufferToBase64(buffer) {
    var bytes = new Uint8Array(buffer);
    var chars = Array.from(bytes).map(function (b) { return String.fromCharCode(b); });
    return btoa(chars.join(""));
}
exports.arrayBufferToBase64 = arrayBufferToBase64;
function base64ToArrayBuffer(base64) {
    var binary_string = atob(base64);
    var len = binary_string.length;
    var bytes = new Uint8Array(len);
    for (var i = 0, end = len; i < end; i++) {
        bytes[i] = binary_string.charCodeAt(i);
    }
    return bytes.buffer;
}
exports.base64ToArrayBuffer = base64ToArrayBuffer;
function decode_base64(input) {
    var bytes = base64ToArrayBuffer(input.__ndarray__);
    var dtype = input.dtype;
    var shape = input.shape;
    var array;
    if (dtype in exports.ARRAY_TYPES)
        array = new (exports.ARRAY_TYPES[dtype])(bytes);
    else
        throw new Error("unknown dtype: " + dtype);
    return [array, shape];
}
exports.decode_base64 = decode_base64;
function encode_base64(array, shape) {
    var b64 = arrayBufferToBase64(array.buffer);
    var name = arrayName(array);
    var dtype;
    if (name in exports.DTYPES)
        dtype = exports.DTYPES[name];
    else
        throw new Error("unknown array type: " + name);
    var data = {
        __ndarray__: b64,
        shape: shape,
        dtype: dtype,
    };
    return data;
}
exports.encode_base64 = encode_base64;
function decode_column_data(data, buffers) {
    if (buffers === void 0) { buffers = []; }
    var new_data = {};
    var new_shapes = {};
    for (var k in data) {
        // might be array of scalars, or might be ragged array or arrays
        var v = data[k];
        if (types_1.isArray(v)) {
            // v is just a regular array of scalars
            if (v.length == 0 || !(types_1.isObject(v[0]) || types_1.isArray(v[0]))) {
                new_data[k] = v;
                continue;
            }
            // v is a ragged array of arrays
            var arrays = [];
            var shapes = [];
            for (var _i = 0, v_1 = v; _i < v_1.length; _i++) {
                var obj = v_1[_i];
                var _a = process_array(obj, buffers), arr = _a[0], shape = _a[1];
                arrays.push(arr);
                shapes.push(shape);
            }
            new_data[k] = arrays;
            new_shapes[k] = shapes;
            // must be object or array (single array case)
        }
        else {
            var _b = process_array(v, buffers), arr = _b[0], shape = _b[1];
            new_data[k] = arr;
            new_shapes[k] = shape;
        }
    }
    return [new_data, new_shapes];
}
exports.decode_column_data = decode_column_data;
function encode_column_data(data, shapes) {
    var new_data = {};
    for (var k in data) {
        var v = data[k];
        var new_v = void 0;
        if (types_1.isTypedArray(v)) {
            new_v = encode_base64(v, shapes != null ? shapes[k] : undefined);
        }
        else if (types_1.isArray(v)) {
            var new_array = [];
            for (var i = 0, end = v.length; i < end; i++) {
                var item = v[i];
                if (types_1.isTypedArray(item)) {
                    var shape = shapes != null && shapes[k] != null ? shapes[k][i] : undefined;
                    new_array.push(encode_base64(item, shape));
                }
                else
                    new_array.push(item);
            }
            new_v = new_array;
        }
        else
            new_v = v;
        new_data[k] = new_v;
    }
    return new_data;
}
exports.encode_column_data = encode_column_data;
