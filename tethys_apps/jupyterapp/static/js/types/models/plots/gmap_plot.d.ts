import { PlotCanvas } from "./plot_canvas";
import { Plot, PlotView } from "./plot";
import * as p from "core/properties";
import { Model } from "../../model";
export declare namespace MapOptions {
    interface Attrs extends Model.Attrs {
        lat: number;
        lng: number;
        zoom: number;
    }
    interface Props extends Model.Props {
        lat: p.Property<number>;
        lng: p.Property<number>;
        zoom: p.Property<number>;
    }
}
export interface MapOptions extends MapOptions.Attrs {
}
export declare class MapOptions extends Model {
    properties: MapOptions.Props;
    constructor(attrs?: Partial<MapOptions.Attrs>);
    static initClass(): void;
}
export declare namespace GMapOptions {
    interface Attrs extends MapOptions.Attrs {
        map_type: string;
        scale_control: boolean;
        styles: string;
        tilt: number;
    }
    interface Props extends MapOptions.Props {
        map_type: p.Property<string>;
        scale_control: p.Property<boolean>;
        styles: p.Property<string>;
        tilt: p.Property<number>;
    }
}
export interface GMapOptions extends GMapOptions.Attrs {
}
export declare class GMapOptions extends MapOptions {
    properties: GMapOptions.Props;
    constructor(attrs?: Partial<GMapOptions.Attrs>);
    static initClass(): void;
}
export declare class GMapPlotView extends PlotView {
    model: GMapPlot;
}
export declare namespace GMapPlot {
    interface Attrs extends Plot.Attrs {
        map_options: GMapOptions;
        api_key: string;
    }
    interface Props extends Plot.Props {
        map_options: p.Property<GMapOptions>;
        api_key: p.Property<string>;
    }
}
export interface GMapPlot extends GMapPlot.Attrs {
}
export declare class GMapPlot extends Plot {
    properties: GMapPlot.Props;
    constructor(attrs?: Partial<GMapPlot.Attrs>);
    static initClass(): void;
    initialize(): void;
    protected _init_plot_canvas(): PlotCanvas;
}
