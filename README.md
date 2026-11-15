# Nikon D7500 firmware research notes

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

## How to validate

You need your own lawfully obtained firmware. Nothing is shipped here.

1. Acquire the official D7500 C 1.12 image and hash it.
2. Decrypt it with the upstream legacy-Nikon tooling.
3. Check the space label at `0x20`, module count `3`, directory size `144`.
4. Verify every module CRC and the package CRC (CRC-16/XMODEM). All must pass.
5. Compare the table SHA-256 values in [FINDINGS.md](FINDINGS.md#2-obfuscation).
6. Recompute `SHA1(body || K8)` if you have K8; the header cannot be checked
   without it.
7. For the feature table, extract UTF-16LE strings and count the exact phrases.
8. For the emulator, run `tools/m0_unicorn.py <decrypted-image>` and expect
   execution at `0x10000000`, then a dispatcher return or a fault at `0x0`.

None of these steps requires modifying or flashing a camera.

## What is deliberately missing

- Firmware binaries, decrypted images, module blobs.
- The XOR tables and the D7500 K8 value.
- Flashing instructions, recovery images, or anything that bypasses update
  verification.

Keys are withheld for legal reasons (see [LEGAL.md](LEGAL.md)). The method to
recover them is public and credited below; the values are not redistributed
here.

K8 is not needed to verify the container, CRC or feature claims. Researchers
who need it for interoperability work can contact the maintainer privately; it
is deliberately not posted in this repository.

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

Code in `tools/`: [MIT](LICENSE).

Text and figures: [CC BY 4.0](LICENSE-docs)
(https://creativecommons.org/licenses/by/4.0/).

Upstream projects keep their own licenses and are not bundled here:
nikon-fw-key-tool (GPL-3.0), Nikon-Expeed-4-and-5-firmware-tool, Unicorn
(BSD-2-Clause), Capstone (BSD-3-Clause).