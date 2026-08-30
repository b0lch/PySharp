# PySharp

PySharp ist eine kleine an C# angelehnte Programmiersprache, die `.therapy` Datein in Python Compiliert.


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
## Demo

A small for-loop demo is included at [examples/for.therapy](examples/for.therapy). Run it like this:

```powershell
& "$env:APPDATA\Python\Python313\Scripts\pysharp.exe" .\examples\for.therapy
```

This demonstrates the `for (int i = 0; i < n; i++) { ... }` translation provided by the example plugin.

If you prefer POSIX shells (macOS/Linux):

```bash
git clone https://github.com/b0lch/PySharp.git
cd PySharp
python3 -m pip install -e .
pysharp examples/hello.therapy
```
