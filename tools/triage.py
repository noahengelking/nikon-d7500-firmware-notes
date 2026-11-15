#!/usr/bin/env python3
"""First-pass structural triage of a suspected Nikon firmware image.

Read-only. Reports size, hash, entropy, string visibility, and whether the
file matches the documented Nikon module-table layout.
"""

from __future__ import annotations

import argparse
import hashlib
import math
import struct
import sys
from pathlib import Path

SPACE32 = b' ' * 32
KEYWORDS = [b'peaking', b'Peaking', b'PEAKING', b'focus', b'NIKON', b'Expeed',
            b'EXPEED', b'menu', b'version', b'D7500']


def shannon(data):
    if not data:
        return 0.0
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    total = float(len(data))
    ent = 0.0
    for c in counts:
        if c:
            p = c / total
            ent -= p * math.log2(p)
    return ent


def crc16_1021(data):
    crc = 0
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def ascii_runs(data, minimum=6):
    runs = []
    cur = []
    for b in data:
        if 32 <= b < 127:
            cur.append(chr(b))
        else:
            if len(cur) >= minimum:
                runs.append(''.join(cur))
            cur = []
    if len(cur) >= minimum:
        runs.append(''.join(cur))
    return runs


def utf16_runs(data, minimum=6):
    runs = []
    cur = []
    for i in range(0, len(data) - 1, 2):
        lo, hi = data[i], data[i + 1]
        if hi == 0 and 32 <= lo < 127:
            cur.append(chr(lo))
        else:
            if len(cur) >= minimum:
                runs.append(''.join(cur))
            cur = []
    if len(cur) >= minimum:
        runs.append(''.join(cur))
    return runs


def parse_directory(data, dir_off):
    if dir_off + 16 > len(data):
        return None
    count, dsize = struct.unpack_from('>II', data, dir_off)
    if not (0 < count <= 256):
        return None
    if dsize != 48 + 32 * count:
        return None
    if dir_off + dsize > len(data):
        return None
    entries = []
    for i in range(count):
        base = dir_off + 16 + i * 32
        raw = data[base:base + 16]
        name = raw.split(b'\x00')[0]
        if not name or any(c < 32 or c > 126 for c in name):
            return None
        off, length = struct.unpack_from('>II', data, base + 16)
        entries.append((name.decode('ascii'), off, length))
    return count, dsize, entries


def report(path):
    data = Path(path).read_bytes()
    size = len(data)
    print('file      : %s' % path)
    print('size      : %d bytes (0x%X)' % (size, size))
    print('sha256    : %s' % hashlib.sha256(data).hexdigest())
    print('head      : %s' % data[:32].hex())
    print('aligned   : %s' % ('yes' if size % 0x1000 == 0 else 'no'))

    ent = shannon(data)
    blocks = [shannon(data[i:i + 4096]) for i in range(0, size, 4096)]
    print('entropy   : whole %.3f   blocks min %.3f max %.3f' % (
          ent, min(blocks), max(blocks)))
    if ent > 7.9:
        print('            dense throughout - encrypted or compressed')
    elif ent < 5.5:
        print('            structured - likely plaintext or light packing')

    for label_off in (0x20, 0x260):
        if data[label_off:label_off + 32] == SPACE32:
            print('label     : 32 spaces found at 0x%X' % label_off)
            parsed = parse_directory(data, label_off + 32)
            if parsed:
                count, dsize, entries = parsed
                print('directory : %d modules, size 0x%X' % (count, dsize))
                for name, off, length in entries[:12]:
                    print('   %-16s off 0x%-8X len 0x%-8X' % (name, off, length))
                first = entries[0]
                body = label_off
                start = body + first[1]
                end = start + first[2]
                if end <= size and first[2] > 2:
                    calc = crc16_1021(data[start:end - 2])
                    stored = struct.unpack_from('>H', data, end - 2)[0]
                    print('crc check : module %s calc 0x%04X stored 0x%04X %s' % (
                          first[0], calc, stored, 'MATCH' if calc == stored else 'mismatch'))
            else:
                print('directory : does not parse at 0x%X' % (label_off + 32))

    ascii_list = ascii_runs(data)
    utf16_list = utf16_runs(data)
    print('strings   : %d ascii (6+), %d utf16 (6+)' % (len(ascii_list), len(utf16_list)))
    hits = {}
    for kw in KEYWORDS:
        n = data.count(kw)
        if n:
            hits[kw.decode('ascii', 'replace')] = n
    if hits:
        print('keywords  : %s' % ', '.join('%s=%d' % (k, v) for k, v in sorted(hits.items())))
    else:
        print('keywords  : none found (expected if encrypted)')
    print('sample    : %s' % ' | '.join(ascii_list[:6]))


def main():
    ap = argparse.ArgumentParser(description='Structural triage of a firmware image')
    ap.add_argument('files', nargs='+')
    args = ap.parse_args()
    for f in args.files:
        try:
            report(f)
        except OSError as exc:
            print('cannot read %s: %s' % (f, exc))
            return 2
        print('')
    return 0


if __name__ == '__main__':
    sys.exit(main())
