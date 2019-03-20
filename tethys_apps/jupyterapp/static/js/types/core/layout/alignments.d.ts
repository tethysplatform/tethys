import { LayoutCanvas as Layout } from "./layout_canvas";
import { Constraint } from "./solver";
export declare function vstack(container: Layout, children: Layout[]): Constraint[];
export declare function hstack(container: Layout, children: Layout[]): Constraint[];
