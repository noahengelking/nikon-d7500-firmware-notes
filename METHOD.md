# Method

1. **Acquire** official Nikon firmware images and hash them; keep originals
   read-only. No third-party mirrors.
2. **Triage** with a read-only structural script: entropy, space label, module
   table sanity, CRC checks.
3. **Decrypt** using the public Nikon legacy XOR tooling. The tables are global
   across the line; no per-camera key is involved in the obfuscation layer.
4. **Validate** by requiring every module CRC and the package CRC to pass. A
   wrong table cannot satisfy both levels.
5. **Recover K8** with a 65,536-candidate keystream search against
   `SHA1(body || K8)`, using the shared raw constant from the upstream tool.
6. **Repack** a validation-only image: change bytes, rebuild module and package
   CRCs, recompute the header digest. Never flash without a donor and a
   recovery path.
7. **Compare features** by extracting UTF-16LE UI strings from decrypted
   sibling bodies and diffing exact phrases.
8. **Emulate** with Unicorn: map modules at inferred bases, start at the vector
   table, trace until an unmapped access. Treat every inferred base as a
   hypothesis until code executes.

## Tooling

- Python 3, NumPy for fast XOR/CRC work.
- Capstone for ARM/Thumb disassembly.
- Unicorn for the M0 harness.
- libgphoto2/gphoto2 for read-only PTP.
- Upstream: `nikon-fw-key-tool` and `Nikon-Expeed-4-and-5-firmware-tool`.

## Rules that mattered

- Never trust a table without CRC validation.
- Never trust an address without executing it.
- Never trust a string search without checking encoding (UTF-16 vs ASCII).
- Never flash the only body.