# PySharp

PySharp ist eine kleine an C# angelehnte Programmiersprache, die `.therapy` Datein in Python Compiliert.

## Usage


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
