# Credits

This work would not exist without the Nikon firmware community. Direct
dependencies and inspirations:

## Directly used

- **Truman Kletka (`LuoStickmin`)** - [Nikon-Expeed-4-and-5-firmware-tool]
  (https://github.com/LuoStickmin/Nikon-Expeed-4-and-5-firmware-tool) and
  [D750-QEMU](https://github.com/LuoStickmin/D750-QEMU). The K8 method and
  solver, and the QEMU M0/M1 methodology, come from this work.
- **WonderLantern** - [nikon-fw-key-tool]
  (https://github.com/WonderLantern/nikon-fw-key-tool), plus
  [z7-qemu](https://github.com/WonderLantern/z7-qemu) and
  [z9-qemu](https://github.com/WonderLantern/z9-qemu). The legacy container
  description and XOR table recovery originate here.
- **new-Beginner** - [z62-qemu](https://github.com/new-Beginner/z62-qemu), a
  reference for firmware execution and ISP modelling.

## Prior art and inspiration

- **Simeon Pilgrim** - 2011 write-up on decoding Nikon DSLR firmware
  (three-layer XOR, 16 MiB period).
- **CHDK** and **Magic Lantern** - the methodology of loading code, hooking
  functions and never bricking a body.
- The **Nikon Hacker** community, whose archives documented years of Nikon
  firmware patching.

## Tools

- **QEMU**, **Unicorn**, **Capstone**
- **libgphoto2 / gphoto2**
- **Ghidra** (used conceptually; the public write-up does not ship projects)
- **Python / NumPy**

## Correction policy

If a credit is missing or wrong, open an issue. This repository exists to
share findings, not to claim them.