import { Model } from "../../model";
import { Geometry } from "core/geometry";
import { HitTestResult } from "core/hittest";
import { GlyphRendererView } from "../renderers/glyph_renderer";
import { ColumnarDataSource } from "../sources/columnar_data_source";
export declare abstract class SelectionPolicy extends Model {
    abstract hit_test(geometry: Geometry, renderer_views: GlyphRendererView[]): HitTestResult;
    do_selection(hit_test_result: HitTestResult, source: ColumnarDataSource, final: boolean, append: boolean): boolean;
}
export declare class IntersectRenderers extends SelectionPolicy {
    hit_test(geometry: Geometry, renderer_views: GlyphRendererView[]): HitTestResult;
}
export declare class UnionRenderers extends SelectionPolicy {
    hit_test(geometry: Geometry, renderer_views: GlyphRendererView[]): HitTestResult;
}
