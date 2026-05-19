# Toy Compiler

A minimal expression compiler built as Week 0 Day 6 of my MLIR
learning journey. Compiles arithmetic expressions over identifiers
and numbers into SSA-form pseudo-assembly.

## Pipeline

source string
  → tokenizer (turns characters into tokens)
  → parser    (recursive descent; builds an AST)
  → codegen   (walks the AST, emits pseudo-assembly)
pseudo-assembly

## Grammar

expr   = term (('+' | '-') term)*
term   = factor ('*' factor)*
factor = NUMBER | IDENT | '(' expr ')'

## Example

Input:  (a + b) * c

Output:
  LOAD r0, a
  LOAD r1, b
  ADD r2, r0, r1
  LOAD r3, c
  MUL r4, r2, r3

Note: every register is assigned exactly once — the output is
already in SSA form, simply because each AST node allocates a
fresh register.

## Supported

- Integer literals
- Identifiers (variables, used as opaque names)
- Operators: + - *
- Parenthesized sub-expressions
- Arbitrary nesting and precedence

## Not yet supported

- Division
- Unary operators (e.g., -x)
- Function calls
- Multi-statement programs

## How to run

python compilet_toy.py

Edit the test_cases list at the bottom to try other inputs.

## What I learned

- How recursive descent parsing handles precedence purely
  through the call structure of the grammar functions.
- Why SSA "falls out of" code generation when you always allocate
  a fresh register — you don't have to design for it; you just
  can't avoid it.
- The compiler pipeline (source → tokens → AST → IR) is the
  same shape at toy scale and industrial scale.

## What's next

Day 7 will add optimization passes on the AST (constant folding,
strength reduction, algebraic simplification) before code
generation.
