# PySharp

PySharp is a small C#-inspired language that transpiles `.therapy` files into Python.

## Usage

Install the project in editable mode:

```bash
python -m pip install -e .
```

Then run a `.therapy` file. On PowerShell, use this command if the script is not on PATH:

```powershell
.\pysharp .\examples\hello.therapy
```

If `pysharp` is not recognized, use the installed launcher directly:

```powershell
& "$env:APPDATA\Python\Python313\Scripts\pysharp.exe" .\examples\hello.therapy
```

This will compile the `.therapy` file, generate a Python file, and run it.

## Quick start (Windows)

Copy-paste these commands from a PowerShell prompt:

```powershell
git clone https://github.com/b0lch/PySharp.git
cd PySharp
python -m pip install -e .
& "$env:APPDATA\Python\Python313\Scripts\pysharp.exe" .\examples\hello.therapy
```

If the `pysharp` launcher is on PATH you can run the shorter form:

```powershell
pysharp .\examples\hello.therapy
```

If you prefer POSIX shells (macOS/Linux):

```bash
git clone https://github.com/b0lch/PySharp.git
cd PySharp
python3 -m pip install -e .
pysharp examples/hello.therapy
```
