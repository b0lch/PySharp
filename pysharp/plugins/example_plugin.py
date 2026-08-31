from pysharp.extensions import register_type, register_statement


# Add a custom type alias
register_type("long", "int")


def say_handler(statement: str):
    # Convert: say "Hello"  ->  print("Hello")
    import re

    m = re.match(r'^say\s+"(.*)"$', statement)
    if m:
        text = m.group(1)
        return f'print("{text}")'

    return None


register_statement(say_handler)
