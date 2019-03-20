"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var signaling_1 = require("./signaling");
var property_mixins = require("./property_mixins");
var refs_1 = require("./util/refs");
var p = require("./properties");
var string_1 = require("./util/string");
var array_1 = require("./util/array");
var object_1 = require("./util/object");
var types_1 = require("./util/types");
var eq_1 = require("./util/eq");
var HasProps = /** @class */ (function (_super) {
    tslib_1.__extends(HasProps, _super);
    function HasProps(attrs) {
        if (attrs === void 0) { attrs = {}; }
        var _this = _super.call(this) || this;
        _this._subtype = undefined;
        _this.document = null;
        _this.destroyed = new signaling_1.Signal0(_this, "destroyed");
        _this.change = new signaling_1.Signal0(_this, "change");
        _this.transformchange = new signaling_1.Signal0(_this, "transformchange");
        _this.attributes = {};
        _this.properties = {};
        _this._set_after_defaults = {};
        _this._pending = false;
        _this._changing = false;
        for (var name_1 in _this.props) {
            var _a = _this.props[name_1], type = _a.type, default_value = _a.default_value;
            if (type != null)
                _this.properties[name_1] = new type(_this, name_1, default_value);
            else
                throw new Error("undefined property type for " + _this.type + "." + name_1);
        }
        // auto generating ID
        if (attrs.id == null)
            _this.setv({ id: string_1.uniqueId() }, { silent: true });
        var deferred = attrs.__deferred__ || false;
        if (deferred) {
            attrs = object_1.clone(attrs);
            delete attrs.__deferred__;
        }
        _this.setv(attrs, { silent: true });
        // allowing us to defer initialization when loading many models
        // when loading a bunch of models, we want to do initialization as a second pass
        // because other objects that this one depends on might not be loaded yet
        if (!deferred)
            _this.finalize();
        return _this;
    }
    HasProps.initClass = function () {
        this.prototype.type = "HasProps";
        this.prototype.props = {};
        this.prototype.mixins = [];
        this.define({
            id: [p.Any],
        });
    };
    // }}}
    HasProps._fix_default = function (default_value, _attr) {
        if (default_value === undefined)
            return undefined;
        else if (types_1.isFunction(default_value))
            return default_value;
        else if (!types_1.isObject(default_value))
            return function () { return default_value; };
        else {
            //logger.warn(`${this.prototype.type}.${attr} uses unwrapped non-primitive default value`)
            if (types_1.isArray(default_value))
                return function () { return array_1.copy(default_value); };
            else
                return function () { return object_1.clone(default_value); };
        }
    };
    HasProps.define = function (obj) {
        var _loop_1 = function (name_2) {
            var prop = obj[name_2];
            if (this_1.prototype.props[name_2] != null)
                throw new Error("attempted to redefine property '" + this_1.prototype.type + "." + name_2 + "'");
            if (this_1.prototype[name_2] != null)
                throw new Error("attempted to redefine attribute '" + this_1.prototype.type + "." + name_2 + "'");
            Object.defineProperty(this_1.prototype, name_2, {
                // XXX: don't use tail calls in getters/setters due to https://bugs.webkit.org/show_bug.cgi?id=164306
                get: function () {
                    var value = this.getv(name_2);
                    return value;
                },
                set: function (value) {
                    var _a;
                    this.setv((_a = {}, _a[name_2] = value, _a));
                    return this;
                },
                configurable: false,
                enumerable: true,
            });
            var type = prop[0], default_value = prop[1], internal = prop[2];
            var refined_prop = {
                type: type,
                default_value: this_1._fix_default(default_value, name_2),
                internal: internal || false,
            };
            var props = object_1.clone(this_1.prototype.props);
            props[name_2] = refined_prop;
            this_1.prototype.props = props;
        };
        var this_1 = this;
        for (var name_2 in obj) {
            _loop_1(name_2);
        }
    };
    HasProps.internal = function (obj) {
        var _object = {};
        for (var name_3 in obj) {
            var prop = obj[name_3];
            var type = prop[0], default_value = prop[1];
            _object[name_3] = [type, default_value, true];
        }
        this.define(_object);
    };
    HasProps.mixin = function () {
        var names = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            names[_i] = arguments[_i];
        }
        this.define(property_mixins.create(names));
        var mixins = this.prototype.mixins.concat(names);
        this.prototype.mixins = mixins;
    };
    HasProps.mixins = function (names) {
        this.mixin.apply(this, names);
    };
    HasProps.override = function (obj) {
        for (var name_4 in obj) {
            var default_value = this._fix_default(obj[name_4], name_4);
            var value = this.prototype.props[name_4];
            if (value == null)
                throw new Error("attempted to override nonexistent '" + this.prototype.type + "." + name_4 + "'");
            var props = object_1.clone(this.prototype.props);
            props[name_4] = tslib_1.__assign({}, value, { default_value: default_value });
            this.prototype.props = props;
        }
    };
    HasProps.prototype.toString = function () {
        return this.type + "(" + this.id + ")";
    };
    HasProps.prototype.finalize = function () {
        var _this = this;
        // This is necessary because the initial creation of properties relies on
        // model.get which is not usable at that point yet in the constructor. This
        // initializer is called when deferred initialization happens for all models
        // and insures that the Bokeh properties are initialized from Backbone
        // attributes in a consistent way.
        //
        // TODO (bev) split property creation up into two parts so that only the
        // portion of init that can be done happens in HasProps constructor and so
        // that subsequent updates do not duplicate that setup work.
        for (var name_5 in this.properties) {
            var prop = this.properties[name_5];
            prop.update();
            if (prop.spec.transform != null)
                this.connect(prop.spec.transform.change, function () { return _this.transformchange.emit(); });
        }
        this.initialize();
        this.connect_signals();
    };
    HasProps.prototype.initialize = function () { };
    HasProps.prototype.connect_signals = function () { };
    HasProps.prototype.disconnect_signals = function () {
        signaling_1.Signal.disconnectReceiver(this);
    };
    HasProps.prototype.destroy = function () {
        this.disconnect_signals();
        this.destroyed.emit();
    };
    // Create a new model with identical attributes to this one.
    HasProps.prototype.clone = function () {
        return new this.constructor(this.attributes);
    };
    // Set a hash of model attributes on the object, firing `"change"`. This is
    // the core primitive operation of a model, updating the data and notifying
    // anyone who needs to know about the change in state. The heart of the beast.
    HasProps.prototype._setv = function (attrs, options) {
        // Extract attributes and options.
        var check_eq = options.check_eq;
        var silent = options.silent;
        var changes = [];
        var changing = this._changing;
        this._changing = true;
        var current = this.attributes;
        // For each `set` attribute, update or delete the current value.
        for (var attr in attrs) {
            var val = attrs[attr];
            if (check_eq !== false) {
                if (!eq_1.isEqual(current[attr], val))
                    changes.push(attr);
            }
            else
                changes.push(attr);
            current[attr] = val;
        }
        // Trigger all relevant attribute changes.
        if (!silent) {
            if (changes.length > 0)
                this._pending = true;
            for (var i = 0; i < changes.length; i++)
                this.properties[changes[i]].change.emit();
        }
        // You might be wondering why there's a `while` loop here. Changes can
        // be recursively nested within `"change"` events.
        if (changing)
            return;
        if (!silent && !options.no_change) {
            while (this._pending) {
                this._pending = false;
                this.change.emit();
            }
        }
        this._pending = false;
        this._changing = false;
    };
    HasProps.prototype.setv = function (attrs, options) {
        if (options === void 0) { options = {}; }
        for (var key in attrs) {
            if (!attrs.hasOwnProperty(key))
                continue;
            var prop_name = key;
            if (this.props[prop_name] == null)
                throw new Error("property " + this.type + "." + prop_name + " wasn't declared");
            if (!(options != null && options.defaults))
                this._set_after_defaults[key] = true;
        }
        if (!object_1.isEmpty(attrs)) {
            var old = {};
            for (var key in attrs)
                old[key] = this.getv(key);
            this._setv(attrs, options);
            var silent = options.silent;
            if (silent == null || !silent) {
                for (var key in attrs)
                    this._tell_document_about_change(key, old[key], this.getv(key), options);
            }
        }
    };
    HasProps.prototype.getv = function (prop_name) {
        if (this.props[prop_name] == null)
            throw new Error("property " + this.type + "." + prop_name + " wasn't declared");
        else
            return this.attributes[prop_name];
    };
    HasProps.prototype.ref = function () {
        return refs_1.create_ref(this);
    };
    // we only keep the subtype so we match Python;
    // only Python cares about this
    HasProps.prototype.set_subtype = function (subtype) {
        this._subtype = subtype;
    };
    HasProps.prototype.attribute_is_serializable = function (attr) {
        var prop = this.props[attr];
        if (prop == null)
            throw new Error(this.type + ".attribute_is_serializable('" + attr + "'): " + attr + " wasn't declared");
        else
            return !prop.internal;
    };
    // dict of attributes that should be serialized to the server. We
    // sometimes stick things in attributes that aren't part of the
    // Document's models, subtypes that do that have to remove their
    // extra attributes here.
    HasProps.prototype.serializable_attributes = function () {
        var attrs = {};
        for (var name_6 in this.attributes) {
            var value = this.attributes[name_6];
            if (this.attribute_is_serializable(name_6))
                attrs[name_6] = value;
        }
        return attrs;
    };
    HasProps._value_to_json = function (_key, value, _optional_parent_object) {
        if (value instanceof HasProps)
            return value.ref();
        else if (types_1.isArray(value)) {
            var ref_array = [];
            for (var i = 0; i < value.length; i++) {
                var v = value[i];
                ref_array.push(HasProps._value_to_json(i.toString(), v, value));
            }
            return ref_array;
        }
        else if (types_1.isPlainObject(value)) {
            var ref_obj = {};
            for (var subkey in value) {
                if (value.hasOwnProperty(subkey))
                    ref_obj[subkey] = HasProps._value_to_json(subkey, value[subkey], value);
            }
            return ref_obj;
        }
        else
            return value;
    };
    // Convert attributes to "shallow" JSON (values which are themselves models
    // are included as just references)
    HasProps.prototype.attributes_as_json = function (include_defaults, value_to_json) {
        if (include_defaults === void 0) { include_defaults = true; }
        if (value_to_json === void 0) { value_to_json = HasProps._value_to_json; }
        var serializable = this.serializable_attributes();
        var attrs = {};
        for (var key in serializable) {
            if (serializable.hasOwnProperty(key)) {
                var value = serializable[key];
                if (include_defaults)
                    attrs[key] = value;
                else if (key in this._set_after_defaults)
                    attrs[key] = value;
            }
        }
        return value_to_json("attributes", attrs, this);
    };
    // this is like _value_record_references but expects to find refs
    // instead of models, and takes a doc to look up the refs in
    HasProps._json_record_references = function (doc, v, result, recurse) {
        if (v == null) {
        }
        else if (refs_1.is_ref(v)) {
            if (!(v.id in result)) {
                var model = doc.get_model_by_id(v.id);
                HasProps._value_record_references(model, result, recurse);
            }
        }
        else if (types_1.isArray(v)) {
            for (var _i = 0, v_1 = v; _i < v_1.length; _i++) {
                var elem = v_1[_i];
                HasProps._json_record_references(doc, elem, result, recurse);
            }
        }
        else if (types_1.isPlainObject(v)) {
            for (var k in v) {
                if (v.hasOwnProperty(k)) {
                    var elem = v[k];
                    HasProps._json_record_references(doc, elem, result, recurse);
                }
            }
        }
    };
    // add all references from 'v' to 'result', if recurse
    // is true then descend into refs, if false only
    // descend into non-refs
    HasProps._value_record_references = function (v, result, recurse) {
        if (v == null) {
        }
        else if (v instanceof HasProps) {
            if (!(v.id in result)) {
                result[v.id] = v;
                if (recurse) {
                    var immediate = v._immediate_references();
                    for (var _i = 0, immediate_1 = immediate; _i < immediate_1.length; _i++) {
                        var obj = immediate_1[_i];
                        HasProps._value_record_references(obj, result, true);
                    } // true=recurse
                }
            }
        }
        else if (v.buffer instanceof ArrayBuffer) {
        }
        else if (types_1.isArray(v)) {
            for (var _a = 0, v_2 = v; _a < v_2.length; _a++) {
                var elem = v_2[_a];
                HasProps._value_record_references(elem, result, recurse);
            }
        }
        else if (types_1.isPlainObject(v)) {
            for (var k in v) {
                if (v.hasOwnProperty(k)) {
                    var elem = v[k];
                    HasProps._value_record_references(elem, result, recurse);
                }
            }
        }
    };
    // Get models that are immediately referenced by our properties
    // (do not recurse, do not include ourselves)
    HasProps.prototype._immediate_references = function () {
        var result = {};
        var attrs = this.serializable_attributes();
        for (var key in attrs) {
            var value = attrs[key];
            HasProps._value_record_references(value, result, false); // false = no recurse
        }
        return object_1.values(result);
    };
    HasProps.prototype.references = function () {
        var references = {};
        HasProps._value_record_references(this, references, true);
        return object_1.values(references);
    };
    HasProps.prototype._doc_attached = function () { };
    HasProps.prototype.attach_document = function (doc) {
        // This should only be called by the Document implementation to set the document field
        if (this.document != null && this.document != doc)
            throw new Error("models must be owned by only a single document");
        this.document = doc;
        this._doc_attached();
    };
    HasProps.prototype.detach_document = function () {
        // This should only be called by the Document implementation to unset the document field
        this.document = null;
    };
    HasProps.prototype._tell_document_about_change = function (attr, old, new_, options) {
        if (!this.attribute_is_serializable(attr))
            return;
        if (this.document != null) {
            var new_refs = {};
            HasProps._value_record_references(new_, new_refs, false);
            var old_refs = {};
            HasProps._value_record_references(old, old_refs, false);
            var need_invalidate = false;
            for (var new_id in new_refs) {
                if (!(new_id in old_refs)) {
                    need_invalidate = true;
                    break;
                }
            }
            if (!need_invalidate) {
                for (var old_id in old_refs) {
                    if (!(old_id in new_refs)) {
                        need_invalidate = true;
                        break;
                    }
                }
            }
            if (need_invalidate)
                this.document._invalidate_all_models();
            this.document._notify_change(this, attr, old, new_, options);
        }
    };
    HasProps.prototype.materialize_dataspecs = function (source) {
        // Note: this should be moved to a function separate from HasProps
        var data = {};
        for (var name_7 in this.properties) {
            var prop = this.properties[name_7];
            if (!prop.dataspec)
                continue;
            // this skips optional properties like radius for circles
            if (prop.optional && prop.spec.value == null && !(name_7 in this._set_after_defaults))
                continue;
            data["_" + name_7] = prop.array(source);
            // the shapes are indexed by the column name, but when we materialize the dataspec, we should
            // store under the canonical field name, e.g. _image_shape, even if the column name is "foo"
            if (prop.spec.field != null && prop.spec.field in source._shapes)
                data["_" + name_7 + "_shape"] = source._shapes[prop.spec.field];
            if (prop instanceof p.Distance)
                data["max_" + name_7] = array_1.max(data["_" + name_7]);
        }
        return data;
    };
    return HasProps;
}(signaling_1.Signalable()));
exports.HasProps = HasProps;
HasProps.initClass();
