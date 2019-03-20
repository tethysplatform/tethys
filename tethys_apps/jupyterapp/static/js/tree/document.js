"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var base_1 = require("./base");
var version_1 = require("./version");
var logging_1 = require("./core/logging");
var bokeh_events_1 = require("core/bokeh_events");
var has_props_1 = require("./core/has_props");
var signaling_1 = require("./core/signaling");
var refs_1 = require("./core/util/refs");
var serialization_1 = require("./core/util/serialization");
var data_structures_1 = require("./core/util/data_structures");
var array_1 = require("./core/util/array");
var object_1 = require("./core/util/object");
var eq_1 = require("./core/util/eq");
var types_1 = require("./core/util/types");
var layout_dom_1 = require("./models/layouts/layout_dom");
var column_data_source_1 = require("./models/sources/column_data_source");
var model_1 = require("./model");
var EventManager = /** @class */ (function () {
    function EventManager(document /* Document */) {
        this.document = document;
        // Dispatches events to the subscribed models
        this.session = null;
        this.subscribed_models = new data_structures_1.Set();
    }
    EventManager.prototype.send_event = function (event) {
        // Send message to Python via session
        if (this.session != null)
            this.session.send_event(event);
    };
    EventManager.prototype.trigger = function (event) {
        for (var _i = 0, _a = this.subscribed_models.values; _i < _a.length; _i++) {
            var model_id = _a[_i];
            if (event.model_id != null && event.model_id !== model_id)
                continue;
            var model = this.document._all_models[model_id];
            if (model != null)
                model._process_event(event);
        }
    };
    return EventManager;
}());
exports.EventManager = EventManager;
var DocumentChangedEvent = /** @class */ (function () {
    function DocumentChangedEvent(document) {
        this.document = document;
    }
    return DocumentChangedEvent;
}());
exports.DocumentChangedEvent = DocumentChangedEvent;
var ModelChangedEvent = /** @class */ (function (_super) {
    tslib_1.__extends(ModelChangedEvent, _super);
    function ModelChangedEvent(document, model, attr, old, new_, setter_id) {
        var _this = _super.call(this, document) || this;
        _this.model = model;
        _this.attr = attr;
        _this.old = old;
        _this.new_ = new_;
        _this.setter_id = setter_id;
        return _this;
    }
    ModelChangedEvent.prototype.json = function (references) {
        if (this.attr === "id") {
            throw new Error("'id' field should never change, whatever code just set it is wrong");
        }
        var value = this.new_;
        var value_json = has_props_1.HasProps._value_to_json(this.attr, value, this.model);
        var value_refs = {};
        has_props_1.HasProps._value_record_references(value, value_refs, true); // true = recurse
        if (this.model.id in value_refs && this.model !== value) {
            // we know we don't want a whole new copy of the obj we're
            // patching unless it's also the value itself
            delete value_refs[this.model.id];
        }
        for (var id in value_refs) {
            references[id] = value_refs[id];
        }
        return {
            kind: "ModelChanged",
            model: this.model.ref(),
            attr: this.attr,
            new: value_json,
        };
    };
    return ModelChangedEvent;
}(DocumentChangedEvent));
exports.ModelChangedEvent = ModelChangedEvent;
var TitleChangedEvent = /** @class */ (function (_super) {
    tslib_1.__extends(TitleChangedEvent, _super);
    function TitleChangedEvent(document, title, setter_id) {
        var _this = _super.call(this, document) || this;
        _this.title = title;
        _this.setter_id = setter_id;
        return _this;
    }
    TitleChangedEvent.prototype.json = function (_references) {
        return {
            kind: "TitleChanged",
            title: this.title,
        };
    };
    return TitleChangedEvent;
}(DocumentChangedEvent));
exports.TitleChangedEvent = TitleChangedEvent;
var RootAddedEvent = /** @class */ (function (_super) {
    tslib_1.__extends(RootAddedEvent, _super);
    function RootAddedEvent(document, model, setter_id) {
        var _this = _super.call(this, document) || this;
        _this.model = model;
        _this.setter_id = setter_id;
        return _this;
    }
    RootAddedEvent.prototype.json = function (references) {
        has_props_1.HasProps._value_record_references(this.model, references, true);
        return {
            kind: "RootAdded",
            model: this.model.ref(),
        };
    };
    return RootAddedEvent;
}(DocumentChangedEvent));
exports.RootAddedEvent = RootAddedEvent;
var RootRemovedEvent = /** @class */ (function (_super) {
    tslib_1.__extends(RootRemovedEvent, _super);
    function RootRemovedEvent(document, model, setter_id) {
        var _this = _super.call(this, document) || this;
        _this.model = model;
        _this.setter_id = setter_id;
        return _this;
    }
    RootRemovedEvent.prototype.json = function (_references) {
        return {
            kind: "RootRemoved",
            model: this.model.ref(),
        };
    };
    return RootRemovedEvent;
}(DocumentChangedEvent));
exports.RootRemovedEvent = RootRemovedEvent;
exports.documents = [];
exports.DEFAULT_TITLE = "Bokeh Application";
// This class should match the API of the Python Document class
// as much as possible.
var Document = /** @class */ (function () {
    function Document() {
        exports.documents.push(this);
        this._init_timestamp = Date.now();
        this._title = exports.DEFAULT_TITLE;
        this._roots = [];
        this._all_models = {};
        this._all_models_by_name = new data_structures_1.MultiDict();
        this._all_models_freeze_count = 0;
        this._callbacks = [];
        this.event_manager = new EventManager(this);
        this.idle = new signaling_1.Signal0(this, "idle");
        this._idle_roots = new WeakMap(); // TODO: WeakSet would be better
        this._interactive_timestamp = null;
        this._interactive_plot = null;
    }
    Object.defineProperty(Document.prototype, "layoutables", {
        get: function () {
            return this._roots.filter(function (root) { return root instanceof layout_dom_1.LayoutDOM; });
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Document.prototype, "is_idle", {
        get: function () {
            for (var _i = 0, _a = this.layoutables; _i < _a.length; _i++) {
                var root = _a[_i];
                if (!this._idle_roots.has(root))
                    return false;
            }
            return true;
        },
        enumerable: true,
        configurable: true
    });
    Document.prototype.notify_idle = function (model) {
        this._idle_roots.set(model, true);
        if (this.is_idle) {
            logging_1.logger.info("document idle at " + (Date.now() - this._init_timestamp) + " ms");
            this.idle.emit();
        }
    };
    Document.prototype.clear = function () {
        this._push_all_models_freeze();
        try {
            while (this._roots.length > 0) {
                this.remove_root(this._roots[0]);
            }
        }
        finally {
            this._pop_all_models_freeze();
        }
    };
    Document.prototype.interactive_start = function (plot) {
        if (this._interactive_plot == null) {
            this._interactive_plot = plot;
            this._interactive_plot.trigger_event(new bokeh_events_1.LODStart({}));
        }
        this._interactive_timestamp = Date.now();
    };
    Document.prototype.interactive_stop = function (plot) {
        if (this._interactive_plot != null && this._interactive_plot.id === plot.id) {
            this._interactive_plot.trigger_event(new bokeh_events_1.LODEnd({}));
        }
        this._interactive_plot = null;
        this._interactive_timestamp = null;
    };
    Document.prototype.interactive_duration = function () {
        if (this._interactive_timestamp == null)
            return -1;
        else
            return Date.now() - this._interactive_timestamp;
    };
    Document.prototype.destructively_move = function (dest_doc) {
        if (dest_doc === this) {
            throw new Error("Attempted to overwrite a document with itself");
        }
        dest_doc.clear();
        // we have to remove ALL roots before adding any
        // to the new doc or else models referenced from multiple
        // roots could be in both docs at once, which isn't allowed.
        var roots = array_1.copy(this._roots);
        this.clear();
        for (var _i = 0, roots_1 = roots; _i < roots_1.length; _i++) {
            var root = roots_1[_i];
            if (root.document != null)
                throw new Error("Somehow we didn't detach " + root);
        }
        if (Object.keys(this._all_models).length !== 0) {
            throw new Error("this._all_models still had stuff in it: " + this._all_models);
        }
        for (var _a = 0, roots_2 = roots; _a < roots_2.length; _a++) {
            var root = roots_2[_a];
            dest_doc.add_root(root);
        }
        dest_doc.set_title(this._title);
    };
    // TODO other fields of doc
    Document.prototype._push_all_models_freeze = function () {
        this._all_models_freeze_count += 1;
    };
    Document.prototype._pop_all_models_freeze = function () {
        this._all_models_freeze_count -= 1;
        if (this._all_models_freeze_count === 0) {
            this._recompute_all_models();
        }
    };
    /*protected*/ Document.prototype._invalidate_all_models = function () {
        logging_1.logger.debug("invalidating document models");
        // if freeze count is > 0, we'll recompute on unfreeze
        if (this._all_models_freeze_count === 0) {
            this._recompute_all_models();
        }
    };
    Document.prototype._recompute_all_models = function () {
        var new_all_models_set = new data_structures_1.Set();
        for (var _i = 0, _a = this._roots; _i < _a.length; _i++) {
            var r = _a[_i];
            new_all_models_set = new_all_models_set.union(r.references());
        }
        var old_all_models_set = new data_structures_1.Set(object_1.values(this._all_models));
        var to_detach = old_all_models_set.diff(new_all_models_set);
        var to_attach = new_all_models_set.diff(old_all_models_set);
        var recomputed = {};
        for (var _b = 0, _c = new_all_models_set.values; _b < _c.length; _b++) {
            var m = _c[_b];
            recomputed[m.id] = m;
        }
        for (var _d = 0, _e = to_detach.values; _d < _e.length; _d++) {
            var d = _e[_d];
            d.detach_document();
            if (d instanceof model_1.Model && d.name != null)
                this._all_models_by_name.remove_value(d.name, d);
        }
        for (var _f = 0, _g = to_attach.values; _f < _g.length; _f++) {
            var a = _g[_f];
            a.attach_document(this);
            if (a instanceof model_1.Model && a.name != null)
                this._all_models_by_name.add_value(a.name, a);
        }
        this._all_models = recomputed;
    };
    Document.prototype.roots = function () {
        return this._roots;
    };
    Document.prototype.add_root = function (model, setter_id) {
        logging_1.logger.debug("Adding root: " + model);
        if (array_1.includes(this._roots, model))
            return;
        this._push_all_models_freeze();
        try {
            this._roots.push(model);
        }
        finally {
            this._pop_all_models_freeze();
        }
        this._trigger_on_change(new RootAddedEvent(this, model, setter_id));
    };
    Document.prototype.remove_root = function (model, setter_id) {
        var i = this._roots.indexOf(model);
        if (i < 0)
            return;
        this._push_all_models_freeze();
        try {
            this._roots.splice(i, 1);
        }
        finally {
            this._pop_all_models_freeze();
        }
        this._trigger_on_change(new RootRemovedEvent(this, model, setter_id));
    };
    Document.prototype.title = function () {
        return this._title;
    };
    Document.prototype.set_title = function (title, setter_id) {
        if (title !== this._title) {
            this._title = title;
            this._trigger_on_change(new TitleChangedEvent(this, title, setter_id));
        }
    };
    Document.prototype.get_model_by_id = function (model_id) {
        if (model_id in this._all_models) {
            return this._all_models[model_id];
        }
        else {
            return null;
        }
    };
    Document.prototype.get_model_by_name = function (name) {
        return this._all_models_by_name.get_one(name, "Multiple models are named '" + name + "'");
    };
    Document.prototype.on_change = function (callback) {
        if (!array_1.includes(this._callbacks, callback))
            this._callbacks.push(callback);
    };
    Document.prototype.remove_on_change = function (callback) {
        var i = this._callbacks.indexOf(callback);
        if (i >= 0)
            this._callbacks.splice(i, 1);
    };
    Document.prototype._trigger_on_change = function (event) {
        for (var _i = 0, _a = this._callbacks; _i < _a.length; _i++) {
            var cb = _a[_i];
            cb(event);
        }
    };
    // called by the model
    Document.prototype._notify_change = function (model, attr, old, new_, options) {
        if (attr === 'name') {
            this._all_models_by_name.remove_value(old, model);
            if (new_ != null)
                this._all_models_by_name.add_value(new_, model);
        }
        var setter_id = options != null ? options.setter_id : void 0;
        this._trigger_on_change(new ModelChangedEvent(this, model, attr, old, new_, setter_id));
    };
    Document._references_json = function (references, include_defaults) {
        if (include_defaults === void 0) { include_defaults = true; }
        var references_json = [];
        for (var _i = 0, references_1 = references; _i < references_1.length; _i++) {
            var r = references_1[_i];
            var ref = r.ref();
            ref.attributes = r.attributes_as_json(include_defaults);
            // server doesn't want id in here since it's already in ref above
            delete ref.attributes.id;
            references_json.push(ref);
        }
        return references_json;
    };
    Document._instantiate_object = function (obj_id, obj_type, obj_attrs) {
        var full_attrs = tslib_1.__assign({}, obj_attrs, { id: obj_id, __deferred__: true });
        var model = base_1.Models(obj_type);
        return new model(full_attrs);
    };
    // given a JSON representation of all models in a graph, return a
    // dict of new model objects
    Document._instantiate_references_json = function (references_json, existing_models) {
        // Create all instances, but without setting their props
        var references = {};
        for (var _i = 0, references_json_1 = references_json; _i < references_json_1.length; _i++) {
            var obj = references_json_1[_i];
            var obj_id = obj.id;
            var obj_type = obj.type;
            var obj_attrs = obj.attributes || {};
            var instance = void 0;
            if (obj_id in existing_models)
                instance = existing_models[obj_id];
            else {
                instance = Document._instantiate_object(obj_id, obj_type, obj_attrs);
                if (obj.subtype != null)
                    instance.set_subtype(obj.subtype);
            }
            references[instance.id] = instance;
        }
        return references;
    };
    // if v looks like a ref, or a collection, resolve it, otherwise return it unchanged
    // recurse into collections but not into HasProps
    Document._resolve_refs = function (value, old_references, new_references) {
        function resolve_ref(v) {
            if (refs_1.is_ref(v)) {
                if (v.id in old_references)
                    return old_references[v.id];
                else if (v.id in new_references)
                    return new_references[v.id];
                else
                    throw new Error("reference " + JSON.stringify(v) + " isn't known (not in Document?)");
            }
            else if (types_1.isArray(v))
                return resolve_array(v);
            else if (types_1.isPlainObject(v))
                return resolve_dict(v);
            else
                return v;
        }
        function resolve_array(array) {
            var results = [];
            for (var _i = 0, array_2 = array; _i < array_2.length; _i++) {
                var v = array_2[_i];
                results.push(resolve_ref(v));
            }
            return results;
        }
        function resolve_dict(dict) {
            var resolved = {};
            for (var k in dict) {
                var v = dict[k];
                resolved[k] = resolve_ref(v);
            }
            return resolved;
        }
        return resolve_ref(value);
    };
    // given a JSON representation of all models in a graph and new
    // model instances, set the properties on the models from the
    // JSON
    Document._initialize_references_json = function (references_json, old_references, new_references) {
        var to_update = {};
        for (var _i = 0, references_json_2 = references_json; _i < references_json_2.length; _i++) {
            var obj = references_json_2[_i];
            var obj_id = obj.id;
            var obj_attrs = obj.attributes;
            var was_new = !(obj_id in old_references);
            var instance = !was_new ? old_references[obj_id] : new_references[obj_id];
            // replace references with actual instances in obj_attrs
            var resolved_attrs = Document._resolve_refs(obj_attrs, old_references, new_references);
            to_update[instance.id] = [instance, resolved_attrs, was_new];
        }
        function foreach_depth_first(items, f) {
            var already_started = {};
            function foreach_value(v) {
                if (v instanceof has_props_1.HasProps) {
                    // note that we ignore instances that aren't updated (not in to_update)
                    if (!(v.id in already_started) && v.id in items) {
                        already_started[v.id] = true;
                        var _a = items[v.id], attrs = _a[1], was_new = _a[2];
                        for (var a in attrs) {
                            var e = attrs[a];
                            foreach_value(e);
                        }
                        f(v, attrs, was_new);
                    }
                }
                else if (types_1.isArray(v)) {
                    for (var _i = 0, v_1 = v; _i < v_1.length; _i++) {
                        var e = v_1[_i];
                        foreach_value(e);
                    }
                }
                else if (types_1.isPlainObject(v)) {
                    for (var k in v) {
                        var e = v[k];
                        foreach_value(e);
                    }
                }
            }
            for (var k in items) {
                var _a = items[k], instance = _a[0];
                foreach_value(instance);
            }
        }
        // this first pass removes all 'refs' replacing them with real instances
        foreach_depth_first(to_update, function (instance, attrs, was_new) {
            if (was_new)
                instance.setv(attrs, { silent: true });
        });
        // after removing all the refs, we can run the initialize code safely
        foreach_depth_first(to_update, function (instance, _attrs, was_new) {
            if (was_new)
                instance.finalize();
        });
    };
    Document._event_for_attribute_change = function (changed_obj, key, new_value, doc, value_refs) {
        var changed_model = doc.get_model_by_id(changed_obj.id); // XXX!
        if (!changed_model.attribute_is_serializable(key))
            return null;
        else {
            var event_1 = {
                kind: "ModelChanged",
                model: {
                    id: changed_obj.id,
                    type: changed_obj.type,
                },
                attr: key,
                new: new_value,
            };
            has_props_1.HasProps._json_record_references(doc, new_value, value_refs, true); // true = recurse
            return event_1;
        }
    };
    Document._events_to_sync_objects = function (from_obj, to_obj, to_doc, value_refs) {
        var from_keys = Object.keys(from_obj.attributes); //XXX!
        var to_keys = Object.keys(to_obj.attributes); //XXX!
        var removed = array_1.difference(from_keys, to_keys);
        var added = array_1.difference(to_keys, from_keys);
        var shared = array_1.intersection(from_keys, to_keys);
        var events = [];
        for (var _i = 0, removed_1 = removed; _i < removed_1.length; _i++) {
            var key = removed_1[_i];
            // we don't really have a "remove" event - not sure this ever
            // happens even. One way this could happen is if the server
            // does include_defaults=True and we do
            // include_defaults=false ... in that case it'd be best to
            // just ignore this probably. Warn about it, could mean
            // there's a bug if we don't have a key that the server sent.
            logging_1.logger.warn("Server sent key " + key + " but we don't seem to have it in our JSON");
        }
        for (var _a = 0, added_1 = added; _a < added_1.length; _a++) {
            var key = added_1[_a];
            var new_value = to_obj.attributes[key]; // XXX!
            events.push(Document._event_for_attribute_change(from_obj, key, new_value, to_doc, value_refs));
        }
        for (var _b = 0, shared_1 = shared; _b < shared_1.length; _b++) {
            var key = shared_1[_b];
            var old_value = from_obj.attributes[key]; // XXX!
            var new_value = to_obj.attributes[key]; // XXX!
            if (old_value == null && new_value == null) {
            }
            else if (old_value == null || new_value == null) {
                events.push(Document._event_for_attribute_change(from_obj, key, new_value, to_doc, value_refs));
            }
            else {
                if (!eq_1.isEqual(old_value, new_value))
                    events.push(Document._event_for_attribute_change(from_obj, key, new_value, to_doc, value_refs));
            }
        }
        return events.filter(function (e) { return e != null; });
    };
    // we use this to detect changes during document deserialization
    // (in model constructors and initializers)
    Document._compute_patch_since_json = function (from_json, to_doc) {
        var to_json = to_doc.to_json(false); // include_defaults=false
        function refs(json) {
            var result = {};
            for (var _i = 0, _a = json.roots.references; _i < _a.length; _i++) {
                var obj = _a[_i];
                result[obj.id] = obj;
            }
            return result;
        }
        var from_references = refs(from_json);
        var from_roots = {};
        var from_root_ids = [];
        for (var _i = 0, _a = from_json.roots.root_ids; _i < _a.length; _i++) {
            var r = _a[_i];
            from_roots[r] = from_references[r];
            from_root_ids.push(r);
        }
        var to_references = refs(to_json);
        var to_roots = {};
        var to_root_ids = [];
        for (var _b = 0, _c = to_json.roots.root_ids; _b < _c.length; _b++) {
            var r = _c[_b];
            to_roots[r] = to_references[r];
            to_root_ids.push(r);
        }
        from_root_ids.sort();
        to_root_ids.sort();
        if (array_1.difference(from_root_ids, to_root_ids).length > 0 ||
            array_1.difference(to_root_ids, from_root_ids).length > 0) {
            // this would arise if someone does add_root/remove_root during
            // document deserialization, hopefully they won't ever do so.
            throw new Error("Not implemented: computing add/remove of document roots");
        }
        var value_refs = {};
        var events = [];
        for (var id in to_doc._all_models) {
            if (id in from_references) {
                var update_model_events = Document._events_to_sync_objects(from_references[id], to_references[id], to_doc, value_refs);
                events = events.concat(update_model_events);
            }
        }
        return {
            references: Document._references_json(object_1.values(value_refs), false),
            events: events,
        };
    };
    Document.prototype.to_json_string = function (include_defaults) {
        if (include_defaults === void 0) { include_defaults = true; }
        return JSON.stringify(this.to_json(include_defaults));
    };
    Document.prototype.to_json = function (include_defaults) {
        if (include_defaults === void 0) { include_defaults = true; }
        var root_ids = this._roots.map(function (r) { return r.id; });
        var root_references = object_1.values(this._all_models);
        return {
            version: version_1.version,
            title: this._title,
            roots: {
                root_ids: root_ids,
                references: Document._references_json(root_references, include_defaults),
            },
        };
    };
    Document.from_json_string = function (s) {
        var json = JSON.parse(s);
        return Document.from_json(json);
    };
    Document.from_json = function (json) {
        logging_1.logger.debug("Creating Document from JSON");
        var py_version = json.version; // XXX!
        var is_dev = py_version.indexOf('+') !== -1 || py_version.indexOf('-') !== -1;
        var versions_string = "Library versions: JS (" + version_1.version + ") / Python (" + py_version + ")";
        if (!is_dev && version_1.version !== py_version) {
            logging_1.logger.warn("JS/Python version mismatch");
            logging_1.logger.warn(versions_string);
        }
        else
            logging_1.logger.debug(versions_string);
        var roots_json = json.roots;
        var root_ids = roots_json.root_ids;
        var references_json = roots_json.references;
        var references = Document._instantiate_references_json(references_json, {});
        Document._initialize_references_json(references_json, {}, references);
        var doc = new Document();
        for (var _i = 0, root_ids_1 = root_ids; _i < root_ids_1.length; _i++) {
            var r = root_ids_1[_i];
            doc.add_root(references[r]);
        } // XXX: HasProps
        doc.set_title(json.title); // XXX!
        return doc;
    };
    Document.prototype.replace_with_json = function (json) {
        var replacement = Document.from_json(json);
        replacement.destructively_move(this);
    };
    Document.prototype.create_json_patch_string = function (events) {
        return JSON.stringify(this.create_json_patch(events));
    };
    Document.prototype.create_json_patch = function (events) {
        var references = {};
        var json_events = [];
        for (var _i = 0, events_1 = events; _i < events_1.length; _i++) {
            var event_2 = events_1[_i];
            if (event_2.document !== this) {
                logging_1.logger.warn("Cannot create a patch using events from a different document, event had ", event_2.document, " we are ", this);
                throw new Error("Cannot create a patch using events from a different document");
            }
            json_events.push(event_2.json(references));
        }
        return {
            events: json_events,
            references: Document._references_json(object_1.values(references)),
        };
    };
    Document.prototype.apply_json_patch = function (patch, buffers, setter_id) {
        var _a;
        var references_json = patch.references;
        var events_json = patch.events;
        var references = Document._instantiate_references_json(references_json, this._all_models);
        // The model being changed isn't always in references so add it in
        for (var _i = 0, events_json_1 = events_json; _i < events_json_1.length; _i++) {
            var event_json = events_json_1[_i];
            switch (event_json.kind) {
                case "RootAdded":
                case "RootRemoved":
                case "ModelChanged": {
                    var model_id = event_json.model.id;
                    if (model_id in this._all_models) {
                        references[model_id] = this._all_models[model_id];
                    }
                    else {
                        if (!(model_id in references)) {
                            logging_1.logger.warn("Got an event for unknown model ", event_json.model);
                            throw new Error("event model wasn't known");
                        }
                    }
                    break;
                }
            }
        }
        // split references into old and new so we know whether to initialize or update
        var old_references = {};
        var new_references = {};
        for (var id in references) {
            var value = references[id];
            if (id in this._all_models)
                old_references[id] = value;
            else
                new_references[id] = value;
        }
        Document._initialize_references_json(references_json, old_references, new_references);
        for (var _b = 0, events_json_2 = events_json; _b < events_json_2.length; _b++) {
            var event_json = events_json_2[_b];
            switch (event_json.kind) {
                case 'ModelChanged': {
                    var patched_id = event_json.model.id;
                    if (!(patched_id in this._all_models)) {
                        throw new Error("Cannot apply patch to " + patched_id + " which is not in the document");
                    }
                    var patched_obj = this._all_models[patched_id];
                    var attr = event_json.attr;
                    var model_type = event_json.model.type;
                    // XXXX currently still need this first branch, some updates (initial?) go through here
                    if (attr === 'data' && model_type === 'ColumnDataSource') {
                        var _c = serialization_1.decode_column_data(event_json.new, buffers), data = _c[0], shapes = _c[1];
                        patched_obj.setv({ _shapes: shapes, data: data }, { setter_id: setter_id });
                    }
                    else {
                        var value = Document._resolve_refs(event_json.new, old_references, new_references);
                        patched_obj.setv((_a = {}, _a[attr] = value, _a), { setter_id: setter_id });
                    }
                    break;
                }
                case 'ColumnDataChanged': {
                    var column_source_id = event_json.column_source.id;
                    if (!(column_source_id in this._all_models)) {
                        throw new Error("Cannot stream to " + column_source_id + " which is not in the document");
                    }
                    var column_source = this._all_models[column_source_id];
                    var _d = serialization_1.decode_column_data(event_json.new, buffers), data = _d[0], shapes = _d[1];
                    if (event_json.cols != null) {
                        for (var k in column_source.data) {
                            if (!(k in data)) {
                                data[k] = column_source.data[k];
                            }
                        }
                        for (var k in column_source._shapes) {
                            if (!(k in shapes)) {
                                shapes[k] = column_source._shapes[k];
                            }
                        }
                    }
                    column_source.setv({
                        _shapes: shapes,
                        data: data,
                    }, {
                        setter_id: setter_id,
                        check_eq: false,
                    });
                    break;
                }
                case 'ColumnsStreamed': {
                    var column_source_id = event_json.column_source.id;
                    if (!(column_source_id in this._all_models)) {
                        throw new Error("Cannot stream to " + column_source_id + " which is not in the document");
                    }
                    var column_source = this._all_models[column_source_id];
                    if (!(column_source instanceof column_data_source_1.ColumnDataSource)) {
                        throw new Error("Cannot stream to non-ColumnDataSource");
                    }
                    var data = event_json.data;
                    var rollover = event_json.rollover;
                    column_source.stream(data, rollover);
                    break;
                }
                case 'ColumnsPatched': {
                    var column_source_id = event_json.column_source.id;
                    if (!(column_source_id in this._all_models)) {
                        throw new Error("Cannot patch " + column_source_id + " which is not in the document");
                    }
                    var column_source = this._all_models[column_source_id];
                    if (!(column_source instanceof column_data_source_1.ColumnDataSource)) {
                        throw new Error("Cannot patch non-ColumnDataSource");
                    }
                    var patches = event_json.patches;
                    column_source.patch(patches);
                    break;
                }
                case 'RootAdded': {
                    var root_id = event_json.model.id;
                    var root_obj = references[root_id];
                    this.add_root(root_obj, setter_id); // XXX: HasProps
                    break;
                }
                case 'RootRemoved': {
                    var root_id = event_json.model.id;
                    var root_obj = references[root_id];
                    this.remove_root(root_obj, setter_id); // XXX: HasProps
                    break;
                }
                case 'TitleChanged': {
                    this.set_title(event_json.title, setter_id);
                    break;
                }
                default:
                    throw new Error("Unknown patch event " + JSON.stringify(event_json));
            }
        }
    };
    return Document;
}());
exports.Document = Document;
