"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var tslib_1 = require("tslib");
var model_1 = require("../../model");
var arrayable_1 = require("core/util/arrayable");
var array_1 = require("core/util/array");
var hittest_1 = require("core/hittest");
var GraphHitTestPolicy = /** @class */ (function (_super) {
    tslib_1.__extends(GraphHitTestPolicy, _super);
    function GraphHitTestPolicy(attrs) {
        return _super.call(this, attrs) || this;
    }
    GraphHitTestPolicy.initClass = function () {
        this.prototype.type = "GraphHitTestPolicy";
    };
    GraphHitTestPolicy.prototype._hit_test_nodes = function (geometry, graph_view) {
        if (!graph_view.model.visible)
            return null;
        var hit_test_result = graph_view.node_view.glyph.hit_test(geometry);
        if (hit_test_result == null)
            return null;
        else
            return graph_view.node_view.model.view.convert_selection_from_subset(hit_test_result);
    };
    GraphHitTestPolicy.prototype._hit_test_edges = function (geometry, graph_view) {
        if (!graph_view.model.visible)
            return null;
        var hit_test_result = graph_view.edge_view.glyph.hit_test(geometry);
        if (hit_test_result == null)
            return null;
        else
            return graph_view.edge_view.model.view.convert_selection_from_subset(hit_test_result);
    };
    return GraphHitTestPolicy;
}(model_1.Model));
exports.GraphHitTestPolicy = GraphHitTestPolicy;
var NodesOnly = /** @class */ (function (_super) {
    tslib_1.__extends(NodesOnly, _super);
    function NodesOnly(attrs) {
        return _super.call(this, attrs) || this;
    }
    NodesOnly.initClass = function () {
        this.prototype.type = 'NodesOnly';
    };
    NodesOnly.prototype.hit_test = function (geometry, graph_view) {
        return this._hit_test_nodes(geometry, graph_view);
    };
    NodesOnly.prototype.do_selection = function (hit_test_result, graph, final, append) {
        if (hit_test_result == null)
            return false;
        var node_selection = graph.node_renderer.data_source.selected;
        node_selection.update(hit_test_result, final, append);
        graph.node_renderer.data_source._select.emit();
        return !node_selection.is_empty();
    };
    NodesOnly.prototype.do_inspection = function (hit_test_result, geometry, graph_view, final, append) {
        if (hit_test_result == null)
            return false;
        var node_inspection = graph_view.model.get_selection_manager().get_or_create_inspector(graph_view.node_view.model);
        node_inspection.update(hit_test_result, final, append);
        // silently set inspected attr to avoid triggering data_source.change event and rerender
        graph_view.node_view.model.data_source.setv({ inspected: node_inspection }, { silent: true });
        graph_view.node_view.model.data_source.inspect.emit([graph_view.node_view, { geometry: geometry }]);
        return !node_inspection.is_empty();
    };
    return NodesOnly;
}(GraphHitTestPolicy));
exports.NodesOnly = NodesOnly;
NodesOnly.initClass();
var NodesAndLinkedEdges = /** @class */ (function (_super) {
    tslib_1.__extends(NodesAndLinkedEdges, _super);
    function NodesAndLinkedEdges(attrs) {
        return _super.call(this, attrs) || this;
    }
    NodesAndLinkedEdges.initClass = function () {
        this.prototype.type = 'NodesAndLinkedEdges';
    };
    NodesAndLinkedEdges.prototype.hit_test = function (geometry, graph_view) {
        return this._hit_test_nodes(geometry, graph_view);
    };
    NodesAndLinkedEdges.prototype.get_linked_edges = function (node_source, edge_source, mode) {
        var node_indices = [];
        if (mode == 'selection') {
            node_indices = node_source.selected.indices.map(function (i) { return node_source.data.index[i]; });
        }
        else if (mode == 'inspection') {
            node_indices = node_source.inspected.indices.map(function (i) { return node_source.data.index[i]; });
        }
        var edge_indices = [];
        for (var i = 0; i < edge_source.data.start.length; i++) {
            if (array_1.contains(node_indices, edge_source.data.start[i]) || array_1.contains(node_indices, edge_source.data.end[i]))
                edge_indices.push(i);
        }
        var linked_edges = hittest_1.create_empty_hit_test_result();
        for (var _i = 0, edge_indices_1 = edge_indices; _i < edge_indices_1.length; _i++) {
            var i = edge_indices_1[_i];
            linked_edges.multiline_indices[i] = [0]; //currently only supports 2-element multilines, so this is all of it
        }
        linked_edges.indices = edge_indices;
        return linked_edges;
    };
    NodesAndLinkedEdges.prototype.do_selection = function (hit_test_result, graph, final, append) {
        if (hit_test_result == null)
            return false;
        var node_selection = graph.node_renderer.data_source.selected;
        node_selection.update(hit_test_result, final, append);
        var edge_selection = graph.edge_renderer.data_source.selected;
        var linked_edges_selection = this.get_linked_edges(graph.node_renderer.data_source, graph.edge_renderer.data_source, 'selection');
        edge_selection.update(linked_edges_selection, final, append);
        graph.node_renderer.data_source._select.emit();
        return !node_selection.is_empty();
    };
    NodesAndLinkedEdges.prototype.do_inspection = function (hit_test_result, geometry, graph_view, final, append) {
        if (hit_test_result == null)
            return false;
        var node_inspection = graph_view.node_view.model.data_source.selection_manager.get_or_create_inspector(graph_view.node_view.model);
        node_inspection.update(hit_test_result, final, append);
        graph_view.node_view.model.data_source.setv({ inspected: node_inspection }, { silent: true });
        var edge_inspection = graph_view.edge_view.model.data_source.selection_manager.get_or_create_inspector(graph_view.edge_view.model);
        var linked_edges = this.get_linked_edges(graph_view.node_view.model.data_source, graph_view.edge_view.model.data_source, 'inspection');
        edge_inspection.update(linked_edges, final, append);
        //silently set inspected attr to avoid triggering data_source.change event and rerender
        graph_view.edge_view.model.data_source.setv({ inspected: edge_inspection }, { silent: true });
        graph_view.node_view.model.data_source.inspect.emit([graph_view.node_view, { geometry: geometry }]);
        return !node_inspection.is_empty();
    };
    return NodesAndLinkedEdges;
}(GraphHitTestPolicy));
exports.NodesAndLinkedEdges = NodesAndLinkedEdges;
NodesAndLinkedEdges.initClass();
var EdgesAndLinkedNodes = /** @class */ (function (_super) {
    tslib_1.__extends(EdgesAndLinkedNodes, _super);
    function EdgesAndLinkedNodes(attrs) {
        return _super.call(this, attrs) || this;
    }
    EdgesAndLinkedNodes.initClass = function () {
        this.prototype.type = 'EdgesAndLinkedNodes';
    };
    EdgesAndLinkedNodes.prototype.hit_test = function (geometry, graph_view) {
        return this._hit_test_edges(geometry, graph_view);
    };
    EdgesAndLinkedNodes.prototype.get_linked_nodes = function (node_source, edge_source, mode) {
        var edge_indices = [];
        if (mode == 'selection')
            edge_indices = edge_source.selected.indices;
        else if (mode == 'inspection')
            edge_indices = edge_source.inspected.indices;
        var nodes = [];
        for (var _i = 0, edge_indices_2 = edge_indices; _i < edge_indices_2.length; _i++) {
            var i = edge_indices_2[_i];
            nodes.push(edge_source.data.start[i]);
            nodes.push(edge_source.data.end[i]);
        }
        var node_indices = array_1.uniq(nodes).map(function (i) { return arrayable_1.indexOf(node_source.data.index, i); });
        var linked_nodes = hittest_1.create_empty_hit_test_result();
        linked_nodes.indices = node_indices;
        return linked_nodes;
    };
    EdgesAndLinkedNodes.prototype.do_selection = function (hit_test_result, graph, final, append) {
        if (hit_test_result == null)
            return false;
        var edge_selection = graph.edge_renderer.data_source.selected;
        edge_selection.update(hit_test_result, final, append);
        var node_selection = graph.node_renderer.data_source.selected;
        var linked_nodes = this.get_linked_nodes(graph.node_renderer.data_source, graph.edge_renderer.data_source, 'selection');
        node_selection.update(linked_nodes, final, append);
        graph.edge_renderer.data_source._select.emit();
        return !edge_selection.is_empty();
    };
    EdgesAndLinkedNodes.prototype.do_inspection = function (hit_test_result, geometry, graph_view, final, append) {
        if (hit_test_result == null)
            return false;
        var edge_inspection = graph_view.edge_view.model.data_source.selection_manager.get_or_create_inspector(graph_view.edge_view.model);
        edge_inspection.update(hit_test_result, final, append);
        graph_view.edge_view.model.data_source.setv({ inspected: edge_inspection }, { silent: true });
        var node_inspection = graph_view.node_view.model.data_source.selection_manager.get_or_create_inspector(graph_view.node_view.model);
        var linked_nodes = this.get_linked_nodes(graph_view.node_view.model.data_source, graph_view.edge_view.model.data_source, 'inspection');
        node_inspection.update(linked_nodes, final, append);
        // silently set inspected attr to avoid triggering data_source.change event and rerender
        graph_view.node_view.model.data_source.setv({ inspected: node_inspection }, { silent: true });
        graph_view.edge_view.model.data_source.inspect.emit([graph_view.edge_view, { geometry: geometry }]);
        return !edge_inspection.is_empty();
    };
    return EdgesAndLinkedNodes;
}(GraphHitTestPolicy));
exports.EdgesAndLinkedNodes = EdgesAndLinkedNodes;
EdgesAndLinkedNodes.initClass();
