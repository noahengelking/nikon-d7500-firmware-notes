# Nikon D7500 firmware research - findings

Independent, non-commercial research into the Nikon D7500 (EXPEED 5) firmware
container, update verification and feature surface.

**This repository contains no Nikon firmware, no decrypted images, no extracted
modules, no XOR tables and no signing keys.** It contains write-ups, offsets,
hashes and original tooling only. Nothing here is a flashing guide.

## Why

The D7500 is a 2017 DSLR with a closed update format. This project asked three
questions:

1. Can the update container be understood and rebuilt?
2. Can a modified image be made structurally valid?
3. Which features exist in sibling EXPEED 5 bodies but not in the D7500?

All three now have evidence-backed answers. The camera was never flashed.

## Results at a glance

| Area | Result |
| --- | --- |
| Container | Legacy Nikon layout: 32-byte header, space label, module directory, CRC16 |
| Obfuscation | Three global XOR tables, 16 MiB period; same tables across 15 bodies |
| Header digest | `SHA1(body || K8)`; K8 recovered, value withheld here |
| Repack | Version-bumped 1.13 candidate passes every CRC and the digest, offline |
| Features | D850-only: peaking, focus shift, silent LV, negative digitizer, more |
| Peaking in D7500 | Not present, not dormant (UTF-16 UI diff) |
| Emulation | Module loads and executes at `0x10000000`; full boot blocked by missing libs |

Details: [FINDINGS.md](FINDINGS.md). Method: [METHOD.md](METHOD.md).

## What is deliberately missing

- Firmware binaries, decrypted images, module blobs.
- The XOR tables and the D7500 K8 value.
- Flashing instructions, recovery images, or anything that bypasses update
  verification.

Keys are withheld for legal reasons (see [LEGAL.md](LEGAL.md)). The method to
recover them is public and credited below; the values are not redistributed
here.

## Reproducing

You need your own lawfully obtained firmware images. The public upstream tools
do the heavy lifting:

- [nikon-fw-key-tool](https://github.com/WonderLantern/nikon-fw-key-tool)
- [Nikon-Expeed-4-and-5-firmware-tool](https://github.com/LuoStickmin/Nikon-Expeed-4-and-5-firmware-tool)

`tools/triage.py` is a read-only structural report for a firmware candidate.
`tools/m0_unicorn.py` is the emulator harness (Unicorn) - it needs a local
decrypted image path.

## Credits

See [CREDITS.md](CREDITS.md). This work stands directly on the Nikon firmware
reverse-engineering community; nothing here was done in isolation.

## Legal

Read [LEGAL.md](LEGAL.md). Independent research, no affiliation with Nikon.
Nikon, D7500 and EXPEED are trademarks of their respective owners.

## License

Code: MIT. Text and figures: CC BY 4.0. Upstream tools retain their own
licenses.