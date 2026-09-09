#!/usr/bin/env python3
"""Compute or verify the per-line checksum of a Mazda IC As-Built line as shown by FORScan.

Line format:  720-BB-LL D0D1 D2D3 D4CS   (five data bytes, then the checksum byte)
Short lines (e.g. 720-01-09 "0858 5252 35") have fewer data bytes; the last byte is the checksum.

    checksum = (0x07 + 0x20 + block + line + sum(data bytes)) mod 256

where `line` is the two printed decimal digits read as hex (line 10 -> 0x10).
Verified against all 32 lines of an ND2 cluster dump.

Usage:
    asbuilt_line_checksum.py --calc 720-01-01 2BE1 E2E6 80   # data bytes only -> prints checksum 7D
    asbuilt_line_checksum.py 720-01-01 2BE1 E2E6 807D        # verifies a line (last byte = checksum)
    asbuilt_line_checksum.py --file dump.txt                 # verifies every FORScan line in a file
"""
import re
import sys

LINE_RE = re.compile(r"^(?P<addr>7[0-9A-Fa-f]{2}-\d{2}-\d{2})\s+(?P<hex>(?:[0-9A-Fa-f]{2,4}\s*)+)$")


def parse(addr: str, hexgroups):
    _, block, line = addr.split("-")
    data = bytes.fromhex("".join(hexgroups))
    return int(block, 16), int(line, 16), data


def checksum(block: int, line: int, data: bytes) -> int:
    return (0x07 + 0x20 + block + line + sum(data)) & 0xFF


def handle(addr: str, hexgroups, calc_only: bool = False) -> bool:
    block, line, raw = parse(addr, hexgroups)
    if calc_only:
        calc = checksum(block, line, raw)
        full = (raw + bytes([calc])).hex().upper()
        print(f"{addr} {' '.join(hexgroups)} -> checksum {calc:02X}  full line: {addr} {full[0:4]} {full[4:8]} {full[8:12]}")
        return True
    data, given = raw[:-1], raw[-1]
    calc = checksum(block, line, data)
    ok = calc == given
    print(f"{addr} {' '.join(hexgroups)} -> {'OK' if ok else 'MISMATCH'} (calc {calc:02X}, given {given:02X})")
    return ok


def main(argv):
    if len(argv) >= 2 and argv[0] == "--file":
        ok = True
        for ln in open(argv[1], encoding="utf-8"):
            m = LINE_RE.match(ln.strip())
            if m:
                ok &= handle(m.group("addr"), m.group("hex").split())
        sys.exit(0 if ok else 1)
    calc_only = False
    if argv and argv[0] in ("--calc", "-c"):
        calc_only, argv = True, argv[1:]
    if len(argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(0 if handle(argv[0], argv[1:], calc_only) else 1)


if __name__ == "__main__":
    main(sys.argv[1:])
