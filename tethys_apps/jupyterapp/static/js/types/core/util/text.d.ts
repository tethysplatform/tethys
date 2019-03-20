export interface TextMetrics {
    height: number;
    ascent: number;
    descent: number;
}
export declare function get_text_height(font: string): TextMetrics;
