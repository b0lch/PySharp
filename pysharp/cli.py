import argparse
import re
import subprocess
import sys
from pathlib import Path

from pysharp import extensions as _ext


# Load plugins (no-op if package missing)
_ext.load_plugins()


def translate_expression(expression):

    # Operators
    expression = expression.replace("&&", " and ")
    expression = expression.replace("||", " or ")

    # Replace ! but do not replace !=
    expression = re.sub(r"!(?!=)", "not ", expression)

    # Literals
    expression = re.sub(r"\btrue\b", "True", expression)
    expression = re.sub(r"\bfalse\b", "False", expression)
    expression = re.sub(r"\bnull\b", "None", expression)

    # Let plugins transform expressions
    expression = _ext.apply_expression_transformers(expression)

    return expression.strip()


def translate_statement(statement):

    statement = statement.strip()

    if not statement:
        return ""

    # Remove a semicolon at the end.
    if statement.endswith(";"):
        statement = statement[:-1].rstrip()

    if statement.startswith("using "):
        return "import " + statement[6:].strip()

    type_pattern = _ext.get_type_pattern()
    declaration = re.match(
        rf"^({type_pattern})\s+"
        r"([A-Za-z_]\w*)\s*(?:=\s*(.*))?$",
        statement,
    )

    if declaration:
        type_name, variable_name, value = declaration.groups()

        if value is None:
            return f"{variable_name} = None"

        return f"{variable_name} = {translate_expression(value)}"

    # Allow plugins to handle the statement before default translation
    plugin_out = _ext.call_statement_handlers(statement)
    if plugin_out:
        return plugin_out

    # if (condition)
    match = re.match(r"^if\s*\((.*)\)$", statement)
    if match:
        condition = translate_expression(match.group(1))
        return f"if {condition}:"

    # else if (condition)
    match = re.match(r"^else\s+if\s*\((.*)\)$", statement)
    if match:
        condition = translate_expression(match.group(1))
        return f"elif {condition}:"

    # while (condition)
    match = re.match(r"^while\s*\((.*)\)$", statement)
    if match:
        condition = translate_expression(match.group(1))
        return f"while {condition}:"

    # else
    if statement == "else":
        return "else:"

    return translate_expression(statement)


def convert(source);

    output = []
    indentation = 0

    for line_number, original_line in enumerate(source.splitlines(), start=1):
        line = original_line.strip()

        if not line:
            output.append("")
            continue

        # Preserve simple comments.
        if line.startswith("//"):
            output.append("    " * indentation + "#" + line[2:])
            continue

        # Handle:
        #
        # } else {
        #
        if re.match(r"^\}\s*else\s*\{$", line):
            indentation -= 1

            if indentation < 0:
                raise SyntaxError(
                    f"Line {line_number}: unexpected closing brace"
                )

            output.append("    " * indentation + "else:")
            indentation += 1
            continue

        # Handle:
        #
        # } else if (condition) {
        #
        match = re.match(r"^\}\s*else\s+if\s*(\(.*\))\s*\{$", line)
        if match:
            indentation -= 1

            if indentation < 0:
                raise SyntaxError(
                    f"Line {line_number}: unexpected closing brace"
                )

            condition = match.group(1)
            translated = translate_statement(f"else if {condition}")

            output.append("    " * indentation + translated)
            indentation += 1
            continue

        # Handle a closing brace, optionally followed by another statement.
        if line.startswith("}"):
            indentation -= 1

            if indentation < 0:
                raise SyntaxError(
                    f"Line {line_number}: unexpected closing brace"
                )

            line = line[1:].strip()

            if not line:
                continue

        # Handle an opening brace.
        opens_block = line.endswith("{")

        if opens_block:
            line = line[:-1].strip()

        translated = translate_statement(line)

        if translated:
            output.append("    " * indentation + translated)

        if opens_block:
            indentation += 1

    if indentation != 0:
        raise SyntaxError("The file contains an unclosed opening brace")

    return "\n".join(output) + "\n"


def compile_and_run(input_file, keep_generated_file=True):
    """
    Translates, compiles, saves, and runs a .therapy file.
    """

    input_file = Path(input_file)

    if not input_file.exists():
        raise FileNotFoundError(f"File not found: {input_file}")

    if input_file.suffix != ".therapy":
        raise ValueError("PySharp files must use the .therapy extension")

    source = input_file.read_text(encoding="utf-8")
    generated_code = convert(source)

    output_file = input_file.with_suffix(".generated.py")
    output_file.write_text(generated_code, encoding="utf-8")

    print(f"Generated Python: {output_file}")

    # Check syntax before running.
    try:
        compile(
            generated_code,
            filename=str(output_file),
            mode="exec",
        )
    except SyntaxError as error:
        print("\nGenerated Python has a syntax error:")
        print(error)
        print("\nGenerated code:")
        print(generated_code)
        raise SystemExit(1)

    print("Running PySharp program...\n")

    try:
        subprocess.run(
            [sys.executable, str(output_file)],
            check=True,
        )
    finally:
        if not keep_generated_file:
            output_file.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(
        description="Compile and run PySharp .therapy files."
    )

    parser.add_argument(
        "filename",
        help="The .therapy file to compile and run",
    )

    parser.add_argument(
        "--delete-generated",
        action="store_true",
        help="Delete the generated Python file after execution",
    )



    args = parser.parse_args()

    try:
        compile_and_run(
            args.filename,
            keep_generated_file=not args.delete_generated,
        )
    except Exception as error:
        print(f"Error: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
