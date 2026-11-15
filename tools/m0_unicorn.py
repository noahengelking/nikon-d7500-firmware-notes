#!/usr/bin/env python3
"""M0: load D7500 modules at inferred bases and run to the first fault."""
import struct, sys
from unicorn import *
from unicorn.arm_const import *
from capstone import *

DEC = sys.argv[1] if len(sys.argv) > 1 else 'D7500_0112.dec'
FLASH = 0x10000000
CODE  = 0x40000000
RAM   = 0x90000000
ENTRY = 0x10360238

def modules(path):
    d = open(path, 'rb').read()
    cnt, ds = struct.unpack('>II', d[0x40:0x48])
    out = {}
    for i in range(cnt):
        e = 0x50 + i * 32
        name = d[e:e+16].split(b'\x00')[0].decode()
        off, ln = struct.unpack('>II', d[e+16:e+24])
        out[name] = d[0x20+off:0x20+off+ln]
    return out

mods = modules(DEC)
B = [v for k, v in mods.items() if k.startswith('b1450')][0]
A = [v for k, v in mods.items() if k.startswith('a1450')][0]
print('A', len(A), 'B', len(B))

uc = Uc(UC_ARCH_ARM, UC_MODE_ARM)
uc.mem_map(FLASH, 0x2000000)
uc.mem_map(CODE, 0x200000)
uc.mem_map(RAM, 0x8000000)
uc.mem_write(FLASH, B)
uc.mem_write(CODE, A)
uc.reg_write(UC_ARM_REG_SP, RAM + 0x1000000)
uc.reg_write(UC_ARM_REG_LR, 0xDEADBEEF)
uc.reg_write(UC_ARM_REG_PC, ENTRY)

md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
trace = []
fault = {}

def hook_code(uc, address, size, user):
    if len(trace) < 4000:
        try:
            ins = next(md.disasm(bytes(uc.mem_read(address, size)), address), None)
            trace.append((address, ins.mnemonic + ' ' + ins.op_str if ins else '?'))
        except Exception:
            trace.append((address, '??'))

def hook_unmapped(uc, access, address, size, value, user):
    fault['addr'] = address
    fault['access'] = access
    fault['size'] = size
    return False

uc.hook_add(UC_HOOK_CODE, hook_code)
uc.hook_add(UC_HOOK_MEM_UNMAPPED, hook_unmapped)

err = None
try:
    uc.emu_start(ENTRY, 0xFFFFFFFF, count=2000000)
except UcError as e:
    err = e

print('error:', err)
print('fault:', {k: hex(v) if isinstance(v, int) else v for k, v in fault.items()})
for r in ('R0','R1','R2','R3','R4','R5','SP','LR','PC','CPSR'):
    try:
        print('%-5s %08X' % (r, uc.reg_read(getattr(unicorn.arm_const, 'UC_ARM_REG_'+r))))
    except Exception:
        pass
print('--- last trace ---')
for a, t in trace[-30:]:
    print('%08X  %s' % (a, t))
print('trace len', len(trace))
