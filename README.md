# Rubin GPU Test

Small, dependency-free GPU diagnostics for Windows, Linux, and Termux on Android. It prints a clean terminal report, detects available adapters, checks root access on Termux without opening a `su` prompt, probes graphics APIs, and runs a safe repeatable responsiveness test. It does not modify drivers, overclock hardware, or write files.

## Run

Windows PowerShell:

```powershell
python .\gpu_test.py
```

Linux, Arch, Fedora, Debian, Alpine, and other distributions:

```bash
python3 gpu_test.py
```

Termux:

```sh
pkg update && pkg install python curl
curl -fsSL https://gist.githubusercontent.com/itzlalpekhlua/1609d8155b9ee008fc42ab003c07fcba/raw/run-gpu-test-remote.sh | bash
```

JSON output for scripts and support tickets:

```bash
python3 gpu_test.py --json
```

The tool uses optional system utilities when present: `nvidia-smi`, `rocminfo`, `lspci`, `vulkaninfo`, `glxinfo`, and PowerShell CIM on Windows. Python 3.9+ is the only required dependency.

On Arch Linux, the interactive report detects NVIDIA, AMD, or Intel hardware and offers a matching `pacman -S --needed` command. Installation is opt-in; JSON mode never installs packages.

The `ACTIVE` section reports the renderer currently selected by Windows WMI, OpenGL, or Android SurfaceFlinger and labels it hardware accelerated or software/unknown. This is useful on laptops with integrated and discrete adapters.

## License

MIT © Rubin Labs contributors.
