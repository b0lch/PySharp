"""Quick plugin showing one-line syntax additions using register_pattern."""
from pysharp.extensions import register_type, register_pattern

# Simple type alias
register_type("long", "int")

# One-line statement rule: say "Hello" -> print("Hello")
register_pattern(r'^say\s+"(.+)"$', 'print("{1}")')
