"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const ts = require("typescript");
function kind_of(node, kind) {
    return node.kind === kind;
}
function is_CallExpression(node) {
    return kind_of(node, ts.SyntaxKind.CallExpression);
}
function is_Identifier(node) {
    return kind_of(node, ts.SyntaxKind.Identifier);
}
function is_StringLiteral(node) {
    return kind_of(node, ts.SyntaxKind.StringLiteral);
}
function is_require(node) {
    return is_CallExpression(node) &&
        is_Identifier(node.expression) &&
        node.expression.text === "require" &&
        node.arguments.length === 1;
}
function collect_deps(source) {
    function traverse(node) {
        if (is_require(node)) {
            const [arg] = node.arguments;
            if (is_StringLiteral(arg) && arg.text.length > 0)
                deps.push(arg.text);
        }
        ts.forEachChild(node, traverse);
    }
    const deps = [];
    traverse(source);
    return deps;
}
exports.collect_deps = collect_deps;
