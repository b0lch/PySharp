"""
Plugins can call the registration functions below to add new type mappings,
statement handlers, or expression transformers. Plugins placed under
`pysharp.plugins` are auto-imported by `load_plugins()`.
"""
from typing import Callable, Dict, List, Optional
import importlib
import pkgutil
import re

# Type name mapping: pysharp type -> python type name
TYPE_NAMES: Dict[str, str] = {
    "int": "int",
    "string": "str",
    "double": "float",
    "float": "float",
    "bool": "bool",
    "object": "object",
}

# Statement handlers: functions that accept the original statement string
# and return a translated string, or None to pass-through.
StatementHandler = Callable[[str], Optional[str]]
statement_handlers: List[StatementHandler] = []

# Expression transformers: functions that accept an expression and return
# a possibly transformed expression. They are applied in registration order.
ExpressionTransformer = Callable[[str], str]
expression_transformers: List[ExpressionTransformer] = []


def register_type(name: str, py_name: str) -> None:
    """Register or override a type name mapping."""
    TYPE_NAMES[name] = py_name


def register_statement(handler: StatementHandler) -> None:
    """Register a statement handler function."""
    statement_handlers.append(handler)


def register_expression(transformer: ExpressionTransformer) -> None:
    """Register an expression transformer."""
    expression_transformers.append(transformer)


def register_pattern(pattern: str, template: str, flags: int = 0) -> None:
    """Convenience helper to register a simple statement->template rule.

    Example:
      register_pattern(r'^say\\s+\"(.+)\"$', 'print("{1}")')

    The template may include placeholders `{1}`, `{2}`, ... for regex groups.
    """
    regex = re.compile(pattern, flags)

    def handler(statement: str) -> Optional[str]:
        m = regex.match(statement)
        if not m:
            return None

        out = template
        # Replace numbered placeholders
        for i in range(0, (m.lastindex or 0) + 1):
            key = '{%d}' % i
            val = m.group(i) if i != 0 else m.group(0)
            if val is None:
                val = ''
            out = out.replace(key, val)

        return out

    register_statement(handler)


def get_type_pattern() -> str:
    """Return a regex alternation pattern for known type names."""
    # Sort by length desc to avoid partial matches (e.g., "int" vs "integer")
    names = sorted(TYPE_NAMES.keys(), key=lambda s: -len(s))
    return "|".join(names)


def apply_expression_transformers(expr: str) -> str:
    for t in expression_transformers:
        try:
            expr = t(expr)
        except Exception:
            # Fail-safe: ignore plugin errors
            pass
    return expr


def call_statement_handlers(statement: str) -> Optional[str]:
    for h in statement_handlers:
        try:
            out = h(statement)
        except Exception:
            out = None

        if out:
            return out

    return None


def load_plugins() -> None:
    """Import all modules in the `pysharp.plugins` package to activate plugins."""
    try:
        import pysharp.plugins  # noqa: F401
    except Exception:
        return

    package = pysharp.plugins

    for finder, name, ispkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
        try:
            importlib.import_module(name)
        except Exception:
            # Ignore plugin import errors to keep core stable
            pass
