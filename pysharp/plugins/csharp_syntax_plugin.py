"""

Transforms supported (non-exhaustive):
- `var x = expr;` -> `x = expr`
- `Console.WriteLine(...)` -> `print(...)`
- `foreach (var x in coll) {` -> `for x in coll:`
- `class Name {` -> `class Name:`
- strip `public/private/protected/internal/static` prefixes
- `i++` / `i--` -> `i += 1` / `i -= 1`
- ternary `cond ? a : b` -> `a if cond else b`
- null-coalescing `x ?? y` -> `(x if x is not None else y)`
- remove `namespace` and `using static` lines
"""
import re

from pysharp.extensions import (
    register_type,
    register_pattern,
    register_expression,
    register_statement,
)


# Treat `var` as a valid declaration keyword so the core declaration rule matches it.
register_type("var", "object")


# Strip common modifiers (return the rest of the statement)
register_pattern(r'^(?:public|private|protected|internal|static)\s+(.*)$', '{1}')


# Class declarations: `class Foo {` -> `class Foo:`
register_pattern(r'^class\s+([A-Za-z_]\w*)$', 'class {1}:')


# Console.WriteLine -> print
register_pattern(r'^Console\.WriteLine\s*\((.*)\)$', 'print({1})')


# foreach loops
register_pattern(
    r'^foreach\s*\(\s*(?:var|[A-Za-z_]\w*)\s+([A-Za-z_]\w*)\s+in\s+(.*)\)$',
    'for {1} in {2}:',
)


# Increment / decrement statements
register_pattern(r'^([A-Za-z_]\w*)\s*\+\+$', '{1} += 1')
register_pattern(r'^([A-Za-z_]\w*)\s*--$', '{1} -= 1')


# Remove namespace and using static lines (no-op in translated Python)
register_pattern(r'^namespace\s+.*$', '')
register_pattern(r'^using\s+static\s+.*$', '')


# Expression transformers
def ternary_transform(expr: str) -> str:
    # Convert `cond ? a : b` into `(a if cond else b)` using a non-greedy regex
    try:
        return re.sub(r"([^?]+?)\?([^:]+?):(.+)", lambda m: f"({m.group(2).strip()} if {m.group(1).strip()} else {m.group(3).strip()})", expr)
    except Exception:
        return expr


def null_coalesce_transform(expr: str) -> str:
    # Convert `x ?? y` into `(x if x is not None else y)`
    try:
        return re.sub(r"([^?\s]+?)\s*\?\?\s*([^\s].+)", lambda m: f"({m.group(1).strip()} if {m.group(1).strip()} is not None else {m.group(2).strip()})", expr)
    except Exception:
        return expr


register_expression(ternary_transform)
register_expression(null_coalesce_transform)


# Try/Catch/Finally
register_pattern(r'^try$', 'try:')
register_pattern(r'^finally$', 'finally:')


def catch_handler(statement: str):
    # catch (Exception e)
    m = re.match(r'^catch\s*\(\s*([A-Za-z_][\w\.]*)\s+([A-Za-z_]\w*)\s*\)\s*$', statement)
    if m:
        ex_type, ex_name = m.groups()
        return f'except {ex_type} as {ex_name}:'
    return None


register_statement(catch_handler)


# using(...) { -> with ... as var:
def using_handler(statement: str):
    m = re.match(r'^using\s*\(\s*(?:var|[A-Za-z_]\w*)\s+([A-Za-z_]\w*)\s*=\s*(.+)\)\s*$', statement)
    if m:
        name, expr = m.groups()
        return f'with {expr} as {name}:'
    return None


register_statement(using_handler)


# Method declarations: strip return type and parameter types
def method_handler(statement: str):
    # captures optional modifiers, return type, name, params
    m = re.match(r'^(?:public|private|protected|internal|static\s+)*([A-Za-z_][\w\<\>\,\s]*)\s+([A-Za-z_]\w*)\s*\((.*)\)\s*$', statement)
    if not m:
        return None

    ret_type, name, params = m.groups()

    # Process params: remove types, keep names
    param_names = []
    params = params.strip()
    if params:
        parts = [p.strip() for p in params.split(',') if p.strip()]
        for part in parts:
            # split by space and take last token as name
            toks = part.split()
            param_names.append(toks[-1])

    param_list = ", ".join(param_names)

    # If method is not static, add self as first arg when inside class; we cannot detect class scope here reliably,
    # so do not add `self` automatically — keep explicit for now.
    return f'def {name}({param_list}):'


register_statement(method_handler)


# Lambda expressions: `x => x + 1` -> `lambda x: x + 1`
def lambda_transform(expr: str) -> str:
    try:
        return re.sub(r"([A-Za-z_][\w\s,]*)\s*=>\s*(.+)", lambda m: f"lambda {m.group(1).strip()}: {m.group(2).strip()}", expr)
    except Exception:
        return expr


register_expression(lambda_transform)



# do/while -> translate 'do { ... } while (cond);' into 'while True: ... if not cond: break'
register_pattern(r'^do$', 'while True:')


# switch/case/default
# `switch (expr) {` -> `__switch_expr = expr` then inside `case X:` -> `if __switch_expr == X:`
register_pattern(r'^switch\s*\((.*)\)$', '__switch_expr = {1}')
register_pattern(r'^case\s+(.*)\s*:$', 'if __switch_expr == {1}:')
register_pattern(r'^default\s*:$', 'else:')


# Extended for variants: <=, >= and decrementing loops
register_pattern(
    r'^for\s*\(\s*(?:int|var|[A-Za-z_]\w*)\s+([A-Za-z_]\w*)\s*=\s*(.+?)\s*;\s*\1\s*<=\s*(.+?)\s*;\s*\1\+\+\s*\)$',
    'for {1} in range({2}, ({3}) + 1):',
)

register_pattern(
    r'^for\s*\(\s*(?:int|var|[A-Za-z_]\w*)\s+([A-Za-z_]\w*)\s*=\s*(.+?)\s*;\s*\1\s*>=\s*(.+?)\s*;\s*\1\-\-\s*\)$',
    'for {1} in range({2}, ({3}) - 1, -1):',
)

