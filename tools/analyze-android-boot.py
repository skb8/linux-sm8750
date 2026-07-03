#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0
"""Small Android boot.img analyzer for OnePlus 13 bringup.

This intentionally avoids Android build-system dependencies. It extracts the
parts we need for kernel bringup: boot header, cmdline, kernel, ramdisk when
present, possible IKCONFIG, and strings useful for firmware/driver mapping.
"""

from __future__ import annotations

import argparse
import gzip
import os
import re
import shutil
import struct
import subprocess
from pathlib import Path

BOOT_MAGIC = b"ANDROID!"
PAGE_SIZE = 4096


def align(v: int, a: int = PAGE_SIZE) -> int:
    return (v + a - 1) & ~(a - 1)


def u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.returncode, p.stdout


def cstr(raw: bytes) -> str:
    return raw.split(b"\0", 1)[0].decode("utf-8", "replace").strip()


def parse_boot_header(data: bytes) -> dict[str, object]:
    if data[:8] != BOOT_MAGIC:
        raise SystemExit("Not an Android boot image: missing ANDROID! magic")

    # v0/v1/v2 have kernel_addr at offset 12 and page_size at 36.
    # v3/v4 have os_version at offset 16 and header_size at 20.
    maybe_header_size = u32(data, 20)
    maybe_header_version = u32(data, 40)

    if maybe_header_size in (1580, 1584, 4096) and maybe_header_version >= 3:
        version = maybe_header_version
        kernel_size = u32(data, 8)
        ramdisk_size = u32(data, 12)
        os_version = u32(data, 16)
        header_size = maybe_header_size
        cmdline = cstr(data[44:44 + 1536])
        kernel_off = PAGE_SIZE
        ramdisk_off = align(kernel_off + kernel_size)
        return {
            "version": version,
            "kernel_size": kernel_size,
            "ramdisk_size": ramdisk_size,
            "os_version": os_version,
            "header_size": header_size,
            "page_size": PAGE_SIZE,
            "cmdline": cmdline,
            "kernel_off": kernel_off,
            "ramdisk_off": ramdisk_off,
            "has_dtb_in_boot": False,
            "dtb_size": 0,
            "dtb_off": None,
        }

    # Legacy fallback.
    kernel_size = u32(data, 8)
    ramdisk_size = u32(data, 16)
    second_size = u32(data, 24)
    page_size = u32(data, 36) or PAGE_SIZE
    dtb_size = 0
    dtb_off = None
    header_version = u32(data, 1648) if len(data) >= 1652 else 0
    cmdline = cstr(data[64:64 + 512] + data[608:608 + 1024])
    kernel_off = page_size
    ramdisk_off = align(kernel_off + kernel_size, page_size)
    second_off = align(ramdisk_off + ramdisk_size, page_size)
    if header_version >= 2:
        dtb_size = u32(data, 1632)
        dtb_off = align(second_off + second_size, page_size)
    return {
        "version": header_version,
        "kernel_size": kernel_size,
        "ramdisk_size": ramdisk_size,
        "second_size": second_size,
        "page_size": page_size,
        "cmdline": cmdline,
        "kernel_off": kernel_off,
        "ramdisk_off": ramdisk_off,
        "has_dtb_in_boot": bool(dtb_size),
        "dtb_size": dtb_size,
        "dtb_off": dtb_off,
    }


def write_part(data: bytes, off: int, size: int, path: Path) -> None:
    if size <= 0:
        return
    path.write_bytes(data[off:off + size])


def extract_ikconfig(kernel: Path, out: Path) -> str:
    blob = kernel.read_bytes()
    magic = b"IKCFG_ST"
    end = b"IKCFG_ED"
    s = blob.find(magic)
    if s < 0:
        return "not found"
    e = blob.find(end, s)
    if e < 0:
        return "start found, end missing"
    payload = blob[s + len(magic):e]
    try:
        config = gzip.decompress(payload)
        (out / "kernel.config").write_bytes(config)
        return "extracted to bootimg-files/kernel.config"
    except Exception as exc:
        (out / "kernel.config.raw").write_bytes(payload)
        return f"found but gzip failed: {exc}; raw saved"


def strings(path: Path, pattern: str | None = None, limit: int = 300) -> list[str]:
    code, out = run(["strings", str(path)])
    lines = out.splitlines() if code == 0 else []
    if pattern:
        rx = re.compile(pattern, re.I)
        lines = [x for x in lines if rx.search(x)]
    seen = []
    for x in lines:
        if x not in seen:
            seen.append(x)
        if len(seen) >= limit:
            break
    return seen


def unpack_ramdisk(ramdisk: Path, out: Path) -> str:
    if not ramdisk.exists() or ramdisk.stat().st_size == 0:
        return "not present"
    typ = run(["file", "-b", str(ramdisk)])[1].strip()
    rd = out / "ramdisk"
    rd.mkdir(exist_ok=True)

    cmd = None
    if "gzip" in typ.lower():
        cmd = f"gzip -dc {ramdisk} | cpio -idmv"
    elif "lz4" in typ.lower():
        cmd = f"lz4 -dc {ramdisk} | cpio -idmv"
    elif "zstandard" in typ.lower() or "zstd" in typ.lower():
        cmd = f"zstd -dc {ramdisk} | cpio -idmv"
    elif "xz" in typ.lower():
        cmd = f"xz -dc {ramdisk} | cpio -idmv"
    else:
        return f"unknown compression: {typ}"

    code, output = run(["bash", "-lc", cmd], cwd=rd)
    files = []
    for root, _, names in os.walk(rd):
        for name in names:
            p = Path(root) / name
            files.append(str(p.relative_to(rd)))
    (out / "ramdisk-files.txt").write_text("\n".join(sorted(files)) + "\n")
    return f"{typ}; unpack {'ok' if code == 0 else 'failed'}; {len(files)} files listed"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--report", required=True, type=Path)
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    data = args.boot.read_bytes()
    hdr = parse_boot_header(data)

    kernel = args.out / "kernel"
    ramdisk = args.out / "ramdisk.cpio"
    dtb = args.out / "dtb"
    write_part(data, int(hdr["kernel_off"]), int(hdr["kernel_size"]), kernel)
    write_part(data, int(hdr["ramdisk_off"]), int(hdr["ramdisk_size"]), ramdisk)
    if hdr.get("dtb_off") is not None:
        write_part(data, int(hdr["dtb_off"]), int(hdr["dtb_size"]), dtb)

    kernel_file = run(["file", "-b", str(kernel)])[1].strip() if kernel.exists() else "missing"
    ramdisk_file = run(["file", "-b", str(ramdisk)])[1].strip() if ramdisk.exists() else "missing"
    ik = extract_ikconfig(kernel, args.out) if kernel.exists() else "kernel missing"
    rd = unpack_ramdisk(ramdisk, args.out)

    interesting = strings(kernel, r"(sm8750|sun|dodge|synaptics|s3910|aa569|wcd|ath12k|qca|bt|nfc|st54|pmic|ucsi|panel|dsi|kgsl|adreno|gmu|ipa|mpss|remoteproc|firmware)", 400) if kernel.exists() else []

    report = []
    report.append("# boot.img analysis for OnePlus 13\n")
    report.append("## Header\n")
    for k in sorted(hdr):
        report.append(f"- `{k}`: `{hdr[k]}`")
    report.append(f"- `kernel_file`: `{kernel_file}`")
    report.append(f"- `ramdisk_file`: `{ramdisk_file}`")
    report.append(f"- `ikconfig`: `{ik}`")
    report.append(f"- `ramdisk_unpack`: `{rd}`")
    report.append("\n## Bringup implications\n")
    if not hdr.get("has_dtb_in_boot"):
        report.append("- This boot.img does not carry a DTB. For exact panel/NFC/audio nodes, also use `vendor_boot.img` and `dtbo.img` from the same slot.")
    if int(hdr.get("ramdisk_size", 0)) == 0:
        report.append("- Ramdisk is empty or absent. Android 13+ often keeps first-stage ramdisk in `init_boot.img` / `vendor_boot.img`.")
    report.append("- Kernel strings below are used to identify firmware names, enabled vendor drivers and missing config symbols.")
    report.append("\n## Interesting kernel strings\n")
    if interesting:
        report.extend([f"- `{x}`" for x in interesting])
    else:
        report.append("- none matched")
    report.append("\n## Files written\n")
    for p in sorted(args.out.glob("*")):
        report.append(f"- `{p}`")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(report) + "\n")


if __name__ == "__main__":
    main()
