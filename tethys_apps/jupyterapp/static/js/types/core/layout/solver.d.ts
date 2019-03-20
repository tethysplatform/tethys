import { Variable, Expression, Constraint, Operator, Strength, Solver as ConstraintSolver } from "kiwi";
export declare type Term = number | Variable | [number, Variable];
export { Variable, Expression, Constraint, Operator, Strength };
export declare const EQ: (...terms: (number | Variable | [number, Variable])[]) => Constraint;
export declare const LE: (...terms: (number | Variable | [number, Variable])[]) => Constraint;
export declare const GE: (...terms: (number | Variable | [number, Variable])[]) => Constraint;
export declare const WEAK_EQ: (...terms: (number | Variable | [number, Variable])[]) => Constraint;
export declare const WEAK_LE: (...terms: (number | Variable | [number, Variable])[]) => Constraint;
export declare const WEAK_GE: (...terms: (number | Variable | [number, Variable])[]) => Constraint;
export interface ComputedVariable {
    readonly value: number;
}
export declare class Solver {
    protected solver: ConstraintSolver;
    constructor();
    clear(): void;
    toString(): string;
    readonly num_constraints: number;
    readonly num_editables: number;
    get_constraints(): Constraint[];
    update_variables(): void;
    has_constraint(constraint: Constraint): boolean;
    add_constraint(constraint: Constraint): void;
    remove_constraint(constraint: Constraint): void;
    add_edit_variable(variable: Variable, strength: number): void;
    remove_edit_variable(variable: Variable): void;
    suggest_value(variable: Variable, value: number): void;
}
