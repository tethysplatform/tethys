import { Model } from "../../model";
import { ColumnarDataSource } from "../sources/columnar_data_source";
export declare namespace LayoutProvider {
    interface Attrs extends Model.Attrs {
    }
    interface Props extends Model.Props {
    }
}
export interface LayoutProvider extends LayoutProvider.Attrs {
}
export declare abstract class LayoutProvider extends Model {
    properties: LayoutProvider.Props;
    constructor(attrs?: Partial<LayoutProvider.Attrs>);
    static initClass(): void;
    abstract get_node_coordinates(graph_source: ColumnarDataSource): [number[], number[]];
    abstract get_edge_coordinates(graph_source: ColumnarDataSource): [[number, number][], [number, number][]];
}
