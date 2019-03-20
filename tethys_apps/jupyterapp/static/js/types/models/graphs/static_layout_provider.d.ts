import { LayoutProvider } from "./layout_provider";
import { ColumnarDataSource } from "../sources/columnar_data_source";
export declare namespace StaticLayoutProvider {
    interface Attrs extends LayoutProvider.Attrs {
        graph_layout: {
            [key: string]: [number, number];
        };
    }
    interface Props extends LayoutProvider.Props {
    }
}
export interface StaticLayoutProvider extends StaticLayoutProvider.Attrs {
}
export declare class StaticLayoutProvider extends LayoutProvider {
    properties: StaticLayoutProvider.Props;
    constructor(attrs?: Partial<StaticLayoutProvider.Attrs>);
    static initClass(): void;
    get_node_coordinates(node_source: ColumnarDataSource): [number[], number[]];
    get_edge_coordinates(edge_source: ColumnarDataSource): [[number, number][], [number, number][]];
}
