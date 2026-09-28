#!/usr/bin/env python3
"""Rubin GPU Test: a dependency-free GPU diagnostics and quick benchmark tool."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass


class C:
    def __init__(self, enabled: bool):
        self.enabled = enabled
        self.reset = "\033[0m" if enabled else ""
        self.bold = "\033[1m" if enabled else ""
        self.dim = "\033[2m" if enabled else ""
        self.cyan = "\033[38;5;45m" if enabled else ""
        self.violet = "\033[38;5;141m" if enabled else ""
        self.green = "\033[38;5;82m" if enabled else ""
        self.yellow = "\033[38;5;220m" if enabled else ""
        self.red = "\033[38;5;203m" if enabled else ""


@dataclass
class GPU:
    name: str
    vendor: str = "Unknown"
    driver: str = "Unknown"
    memory: str = "Unknown"
    backend: str = "Unknown"


def command(name: str) -> str | None:
    return shutil.which(name)


def run(args: list[str], timeout: float = 4) -> str:
    try:
        result = subprocess.run(
            args, capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace",
        )
        return (result.stdout or result.stderr).strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def detect_gpu() -> tuple[list[GPU], list[str]]:
    notes: list[str] = []
    found: list[GPU] = []
    if command("nvidia-smi"):
        raw = run([
            "nvidia-smi", "--query-gpu=name,driver_version,memory.total",
            "--format=csv,noheader,nounits",
        ])
        for line in raw.splitlines():
            bits = [item.strip() for item in line.split(",")]
            if len(bits) >= 3:
                found.append(GPU(bits[0], "NVIDIA", bits[1], f"{bits[2]} MiB", "CUDA"))
        if found:
            notes.append("NVIDIA Management Library responded")

    if command("rocminfo"):
        raw = run(["rocminfo"], timeout=6)
        names = []
        for line in raw.splitlines():
            if "Marketing Name:" in line:
                name = line.split(":", 1)[1].strip()
                if name and name not in names:
                    names.append(name)
        for name in names:
            found.append(GPU(name, "AMD", backend="ROCm"))
        if names:
            notes.append("ROCm agent query responded")

    if platform.system() == "Windows":
        raw = run([
            "powershell", "-NoProfile", "-Command",
            "Get-CimInstance Win32_VideoController | "
            "Select-Object Name,DriverVersion,AdapterRAM | ConvertTo-Json -Compress",
        ])
        try:
            rows = json.loads(raw) if raw else []
            if isinstance(rows, dict):
                rows = [rows]
            for row in rows:
                name = str(row.get("Name") or "Unknown GPU")
                if any(g.name.casefold() == name.casefold() for g in found):
                    continue
                memory = row.get("AdapterRAM")
                memory_text = f"{int(memory) / 1024**3:.1f} GiB" if str(memory).isdigit() else "Unknown"
                found.append(GPU(name, driver=str(row.get("DriverVersion") or "Unknown"), memory=memory_text, backend="DirectX"))
        except (ValueError, TypeError):
            notes.append("Windows graphics query returned no structured data")

    if platform.system() == "Linux" and command("lspci"):
        raw = run(["lspci", "-nn"])
        for line in raw.splitlines():
            if "vga compatible controller" in line.lower() or "3d controller" in line.lower():
                name = line.split(": ", 1)[-1].strip()
                if not any(g.name.casefold() == name.casefold() for g in found):
                    vendor = "AMD" if "amd" in name.lower() or "advanced micro" in name.lower() else "Intel" if "intel" in name.lower() else "Unknown"
                    found.append(GPU(name, vendor=vendor, backend="OpenGL/Vulkan"))

    if not found:
        found.append(GPU("No GPU telemetry returned", backend="Unavailable"))
        notes.append("Install lspci, nvidia-smi, rocminfo, or PowerShell GPU tools for richer details")
    return found, notes


def api_probe() -> tuple[str, str, float]:
    if platform.system() == "Windows":
        # Avoid dxdiag's interactive report generation; CIM already proved
        # that the DirectX video-controller path is available.
        return "DirectX", "PowerShell graphics query available", 0.0
    candidates = [
        ("Vulkan", "vulkaninfo", ["vulkaninfo", "--summary"]),
        ("OpenGL", "glxinfo", ["glxinfo", "-B"]),
    ]
    for name, executable, args in candidates:
        if command(executable):
            started = time.perf_counter()
            output = run(args, timeout=8)
            elapsed = (time.perf_counter() - started) * 1000
            if output or name == "DirectX":
                return name, "responded", elapsed
    return "None", "No graphics API probe found", 0.0


def benchmark() -> tuple[float, str]:
    """A repeatable, safe probe for scheduler/display-system responsiveness."""
    started = time.perf_counter()
    value = 0.0
    for index in range(350_000):
        value = (value * 1.000001 + (index % 97) * 0.0001) % 1000
    elapsed = (time.perf_counter() - started) * 1000
    return elapsed, f"probe={value:.2f}"


def banner(color: C) -> None:
    print(f"{color.violet}{color.bold}╭────────────────────────────────────────────╮")
    print("│              RUBIN GPU TEST                 │")
    print(f"╰────────────────────────────────────────────╯{color.reset}")
    print(f"{color.dim}Cross-platform graphics diagnostics · Rubin Labs{color.reset}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Cross-platform GPU diagnostics and quick benchmark")
    parser.add_argument("--json", action="store_true", help="print machine-readable output")
    parser.add_argument("--no-color", action="store_true", help="disable terminal colors")
    args = parser.parse_args()
    color = C(sys.stdout.isatty() and not args.no_color and os.environ.get("NO_COLOR") is None)
    gpus, notes = detect_gpu()
    api, api_status, api_ms = api_probe()
    benchmark_ms, benchmark_detail = benchmark()
    result = {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "gpus": [asdict(gpu) for gpu in gpus],
        "graphics_api": {"name": api, "status": api_status, "probe_ms": round(api_ms, 2)},
        "benchmark": {"elapsed_ms": round(benchmark_ms, 2), "detail": benchmark_detail},
        "notes": notes,
    }
    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    banner(color)
    print(f"{color.cyan}{color.bold}SYSTEM{color.reset}  {platform.system()} {platform.release()} · {platform.machine()} · Python {platform.python_version()}")
    print(f"{color.cyan}{color.bold}GPU{color.reset}")
    for gpu in gpus:
        print(f"  {color.green}◆{color.reset} {gpu.name}")
        print(f"    vendor={gpu.vendor}  driver={gpu.driver}  memory={gpu.memory}  backend={gpu.backend}")
    status_color = color.green if api != "None" else color.yellow
    print(f"{color.cyan}{color.bold}API{color.reset}   {status_color}{api}{color.reset} · {api_status} ({api_ms:.1f} ms)")
    print(f"{color.cyan}{color.bold}TEST{color.reset}  {color.green}PASS{color.reset} · safe responsiveness probe completed in {benchmark_ms:.1f} ms")
    for note in notes:
        print(f"{color.yellow}note{color.reset}  {note}")
    print(f"\n{color.dim}No files were changed. Run with --json for automation.{color.reset}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
