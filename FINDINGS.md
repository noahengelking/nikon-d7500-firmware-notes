# Findings

All statements below were derived from locally owned, lawfully obtained
firmware images. No firmware or key material is included.

## 1. Container

```
0x00  20-byte header digest
0x14  12-byte per-image field (nonce-like)
0x20  32 ASCII spaces (space label)
0x40  BE32 module count, BE32 directory size, 8 zero bytes
0x50  entries: 16-byte name, BE32 offset, BE32 length, 8 zero bytes
      modules, each ending in a BE16 CRC
      BE16 package CRC, 14 zero bytes
```

D7500 C 1.12 has three modules: `a1450_011100.bin` (~1.0 MB),
`_wma_ver01.11.00` (~0.84 MB) and `b1450_112.bin` (~23 MB).

CRC is CRC-16/XMODEM: polynomial 0x1021, init 0, no reflection, no final XOR.
Every module CRC and the package CRC validate after decryption.

## 2. Obfuscation

```
plain[i] = cipher[i] ^ T1[i & 0xFF] ^ T2[(i >> 8) & 0xFF] ^ T3[(i >> 16) & 0xFF]
```

Body-relative offsets, 16 MiB period, three 256-byte tables. The tables are
global across the Nikon line: T1 was byte-identical across 15 images from
D500, D5600, D7500, D780, D850 and the Z series.

Table SHA-256 values observed (also the upstream regression values):

| Table | SHA-256 |
| --- | --- |
| T1 | `29d2e34239fc33bf0a1054fd3558536ad6429966659f5b387a75f16e9aada431` |
| T2 | `6e87de5da7e42df91db31fae4a899a04bd8f0225171922cc98f74922681766e0` |
| T3 | `3617957facf8b21a5a3de0f3a1f6f27ca20d72c7208b196b2a8bec3076f39b49` |

The tables themselves are not redistributed here; they are available from the
upstream tool for those entitled to use them.

## 3. Header digest and K8

`header[0:20] == SHA1(body || K8)`, where K8 is eight bytes appended to the
body before hashing. K8 is derived from a shared raw constant and a
byte-level keystream, searched over 65,536 candidates against the header.

K8 was recovered for the D7500 and verified against C 1.10, C 1.11 and
C 1.12 - the same key works across all three versions. The value is
**withheld** from this repository.

## 4. Repacking

A validation-only candidate was built by:

- renaming the B module `b1450_112.bin` -> `b1450_113.bin` (version bump);
- flipping one padding byte inside module B;
- recomputing module CRCs, package CRC and the header digest.

The result passes directory parsing, every module CRC, the package CRC and the
header digest. It was **not flashed**. Whether the camera accepts a
version-bumped image is still unknown.

## 5. Feature surface (EXPEED 5)

UI text is UTF-16LE. Presence counts on decrypted images:

| Feature | D7500 | D850 | D500 |
| --- | --- | --- | --- |
| Peaking (colour/level/brightness) | 0 | 5 | 0 |
| Focus shift | 0 | 2 | 0 |
| Silent live view | 0 | 1 | 0 |
| Negative digitizer | 0 | 1 | 0 |
| Portrait impression balance | 0 | 3 | 0 |
| Trim movie / save frame | 0 | 1 / 2 | 0 |
| White balance options | 0 | 1 | 0 |
| Interval priority | 0 | 7 | 0 |
| Power aperture | 5 | 6 | 5 |

Conclusions:

- The D7500 has no peaking, not even dormant UI text.
- The D850 is the feature-rich EXPEED 5 body; the D500's advantages are
  hardware (10 fps, 153-point AF, dual card), not menu features.
- Zebra data structures exist in all three, but zebra has no UI text anywhere;
  it looks like an internal display/driver feature, not a hidden user feature.

## 6. Emulation

Module B starts with a standard ARM vector table. With base `0x10000000`,
reset maps to `0x10360238`, which is valid ARM code. Constants:
`0x10000000` (8192x), `0x40000000` (5297x), `0x90000000` (608x).

Unicorn M0: the image loads and executes; the vector entry behaves like a
library dispatcher, not cold boot. Unknown command values return 1; command
`0x73` enters a computed table write.

Module B is not self-contained: it calls `0x12ADA340` (hash init), `0x3EE2B0`
(memcpy), `0x42A16D` (memcmp) and `0x4968C7` (strcpy), none of which were
located in the available modules at plausible bases. Full boot and
function-level verification are blocked until those libraries or a boot ROM
are available.

## 7. USB/PTP

A read-only PTP session confirmed the test body reports D7500, firmware V1.12
and a 640x424 RGB preview. The serial number is omitted. Live view is blocked
unless the mode dial is P/A/S/M. No settings were changed and nothing was
written.

## 8. Open questions

- Do the external libraries load from a boot ROM, or from a module not in the
  update container?
- Does the camera accept a version-bumped image, and does it read the version
  from the B-module name?
- Is peaking portable from the D850, or does it depend on a different pipeline?
- Which display/OSD hook is reachable from a patched module?