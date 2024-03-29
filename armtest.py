#!/usr/bin/env python
# Sample code for ARM of Unicorn. Nguyen Anh Quynh <aquynh@gmail.com>
# Python sample ported by Loi Anh Tuan <loianhtuan@gmail.com>

from __future__ import print_function
from unicorn import *
from unicorn.arm_const import *

from capstone import *

# code to be emulated
ARM_CODE = b"\x37\x00\xa0\xe3\x03\x10\x42\xe0"  # mov r0, #0x37; sub r1, r2, r3
THUMB_CODE = b"\x83\xb0"  # sub    sp, #0xc
# memory address where emulation starts
ADDRESS = 0x10000


# callback for tracing basic blocks
def hook_block(uc, address, size, user_data):
    print(">>> Tracing basic block at 0x%x, block size = 0x%x" % (address, size))


# callback for tracing instructions
def hook_code(uc, address, size, user_data):
    print(">>> Tracing instruction at 0x%x, instruction size = 0x%x" % (address, size))
    ucmem=uc.mem_read(address,size)
    ucmem=str(ucmem)
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    asms=md.disasm( ucmem,0,1)
    for asm in asms:
        print(asm.op_str)


# Test ARM
def test_arm():
    print("Emulate ARM code")
    try:
        # Initialize emulator in ARM mode
        mu = Uc(UC_ARCH_ARM, UC_MODE_ARM)

        # map 2MB memory for this emulation
        mu.mem_map(ADDRESS, 2 * 1024 * 1024)

        # write machine code to be emulated to memory
        mu.mem_write(ADDRESS, ARM_CODE)

        # initialize machine registers
        mu.reg_write(UC_ARM_REG_R0, 0x1234)
        mu.reg_write(UC_ARM_REG_R2, 0x6789)
        mu.reg_write(UC_ARM_REG_R3, 0x3333)
        mu.reg_write(UC_ARM_REG_APSR, 0xFFFFFFFF)  # All application flags turned on

        # tracing all basic blocks with customized callback
        mu.hook_add(UC_HOOK_BLOCK, hook_block)

        # tracing one instruction at ADDRESS with customized callback
        mu.hook_add(UC_HOOK_CODE, hook_code, begin=ADDRESS, end=ADDRESS)

        # emulate machine code in infinite time
        mu.emu_start(ADDRESS, ADDRESS + len(ARM_CODE))

        # now print out some registers
        print(">>> Emulation done. Below is the CPU context")

        r0 = mu.reg_read(UC_ARM_REG_R0)
        r1 = mu.reg_read(UC_ARM_REG_R1)
        print(">>> R0 = 0x%x" % r0)
        print(">>> R1 = 0x%x" % r1)

    except UcError as e:
        print("ERROR: %s" % e)


def test_thumb():
    print("Emulate THUMB code")
    try:
        # Initialize emulator in thumb mode
        mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)

        # map 2MB memory for this emulation
        mu.mem_map(ADDRESS, 2 * 1024 * 1024)

        # write machine code to be emulated to memory
        mu.mem_write(ADDRESS, THUMB_CODE)

        # initialize machine registers
        mu.reg_write(UC_ARM_REG_SP, 0x1234)

        # tracing all basic blocks with customized callback
        mu.hook_add(UC_HOOK_BLOCK, hook_block)

        # tracing all instructions with customized callback
        mu.hook_add(UC_HOOK_CODE, hook_code)

        # emulate machine code in infinite time
        # Note we start at ADDRESS | 1 to indicate THUMB mode.
        mu.emu_start(ADDRESS | 1, ADDRESS + len(THUMB_CODE))

        # now print out some registers
        print(">>> Emulation done. Below is the CPU context")

        sp = mu.reg_read(UC_ARM_REG_SP)
        print(">>> SP = 0x%x" % sp)

    except UcError as e:
        print("ERROR: %s" % e)

def test_add():
    binary=open("libnative-lib.so","rb").read()
    md=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
    dis_start,dis_end,dis_offset=0x7CEE,0x7d04,0
    print(type(binary))
    print(type(binary[dis_start:dis_end]))
    # instructions=md.disasm(binary[dis_start:dis_end],dis_start)
    # for ins in instructions:
    #     print (hex(ins.address),ins.op_str)

    CODE_START=0x00000000
    MEM_SIZE=2*1024*1024
    SP_START=CODE_START+MEM_SIZE
    try:
        uni=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        uni.mem_map(CODE_START,MEM_SIZE)
        uni.mem_write(CODE_START,binary)
        uni.reg_write(UC_ARM_REG_SP,SP_START)
        uni.reg_write(UC_ARM_REG_R0,100)
        uni.reg_write(UC_ARM_REG_R1,1)
        uni.hook_add(UC_HOOK_CODE, hook_code)
        uni.emu_start(dis_start|1,dis_end)
        r0=uni.reg_read(UC_ARM_REG_R0)
        print(r0)

        pass
    except Exception as e:
        print(e)
        pass


if __name__ == '__main__':
    #test_arm()
    print("=" * 26)
    #est_thumb()
    test_add()