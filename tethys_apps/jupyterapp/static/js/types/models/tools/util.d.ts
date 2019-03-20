import { Renderer } from "../renderers/renderer";
import { GlyphRenderer } from "../renderers/glyph_renderer";
import { GraphRenderer } from "../renderers/graph_renderer";
export declare type DataRenderer = GlyphRenderer | GraphRenderer;
export declare type RendererSpec = DataRenderer[] | "auto" | null;
export declare function compute_renderers(renderers: RendererSpec, all_renderers: Renderer[], names: string[]): DataRenderer[];
