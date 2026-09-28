# Rubin GPU Test

Small, dependency-free GPU diagnostics for Windows and Linux. It prints a clean terminal report, detects NVIDIA/AMD/Intel adapters, probes available graphics APIs, and runs a safe repeatable responsiveness test. It does not modify drivers, overclock hardware, or write files.

## Run

Windows PowerShell:

```powershell
python .\gpu_test.py
```

Linux, Arch, Fedora, Debian, Alpine, and other distributions:

```bash
python3 gpu_test.py
```

JSON output for scripts and support tickets:

```bash
python3 gpu_test.py --json
```

The tool uses optional system utilities when present: `nvidia-smi`, `rocminfo`, `lspci`, `vulkaninfo`, `glxinfo`, and PowerShell CIM on Windows. Python 3.9+ is the only required dependency.

## License

MIT © Rubin Labs contributors.
