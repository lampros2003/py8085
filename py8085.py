##8085 emulator
import sys
import os
import time
import re
import random
import ctypes
import platform
print(platform.architecture()[0])
# Load the shared libraries
current_dir = os.path.dirname(os.path.abspath(__file__))
memaccess = ctypes.CDLL(os.path.join(current_dir, 'memory.dll'))
regaccess = ctypes.CDLL(os.path.join(current_dir, 'registers.dll'))

# Define function prototypes for memory access
memaccess.read_memory.argtypes = [ctypes.c_uint16]
memaccess.read_memory.restype = ctypes.c_uint8
memaccess.write_memory.argtypes = [ctypes.c_uint16, ctypes.c_uint8]

# Define function prototypes for register access
regaccess.read_reg.argtypes = [ctypes.c_uint8]
regaccess.read_reg.restype = ctypes.c_uint8
regaccess.write_reg.argtypes = [ctypes.c_uint8, ctypes.c_uint8]
regaccess.get_flags.restype = ctypes.c_uint8
regaccess.set_flags.argtypes = [ctypes.c_uint8]
regaccess.get_PC.restype = ctypes.c_uint16
regaccess.set_PC.argtypes = [ctypes.c_uint16]
regaccess.get_SP.restype = ctypes.c_uint16
regaccess.set_SP.argtypes = [ctypes.c_uint16]

class CPU8085:
    def __init__(self):
        # Initialize registers via C (optional)
        self.set_PC(0)
        self.set_SP(0xF000) # Stack pointer
        self.set_flags(0)

    # Fetch instruction from memory
    def fetch_instruction(self):
        byte = memaccess.read_memory(self.PC)
        self.PC += 1
        return byte

    # Memory access methods
    def read_memory(self, address):
        return memaccess.read_memory(address)

    def write_memory(self, address, value):
        memaccess.write_memory(address, value)

    # Register access methods
    def read_register(self, regname):
        switcher = {
            'A': 0,
            'B': 1,
            'C': 2,
            'D': 3,
            'E': 4,
            'H': 5,
            'L': 6,
            'M': 7
        }
        return regaccess.read_reg(switcher.get(regname, -1))

    def write_register(self, regname, value):
        switcher = {
            'A': 0,
            'B': 1,
            'C': 2,
            'D': 3,
            'E': 4,
            'H': 5,
            'L': 6,
            'M': 7
        }
        regaccess.write_reg(switcher.get(regname, -1), value)

    def get_flags(self):
        return regaccess.get_flags()

    def set_flags(self, value):
        regaccess.set_flags(value)

    def get_PC(self):
        return regaccess.get_PC()

    def set_PC(self, value):
        regaccess.set_PC(value)

    def get_SP(self):
        return regaccess.get_SP()

    def set_SP(self, value):
        regaccess.set_SP(value)

    def run(self):
        while True:
            opcode = self.fetch_instruction()
            print(f"Opcode: {opcode}")
            if opcode == 0x76:
                break

def test_cpu8085():
    cpu = CPU8085()

    # Test writing and reading registers
    cpu.write_register('A', 0x12)
    assert cpu.read_register('A') == 0x12, "Register A test failed"

    cpu.write_register('B', 0x34)
    assert cpu.read_register('B') == 0x34, "Register B test failed"

    # Test setting and getting flags
    cpu.set_flags(0b10101010)
    assert cpu.get_flags() == 0b10101010, "Flags test failed"

    # Test setting and getting PC
    cpu.set_PC(0x1234)
    assert cpu.get_PC() == 0x1234, "PC test failed"

    # Test setting and getting SP
    cpu.set_SP(0x5678)
    assert cpu.get_SP() == 0x5678, "SP test failed"

    # Test writing and reading memory
    cpu.write_memory(0x1000, 0x34)
    assert cpu.read_memory(0x1000) == 0x34, "Memory test failed"

    # Test fetching instruction
    cpu.set_PC(0x1000)
    assert cpu.fetch_instruction() == 0x34, "Fetch instruction test failed"

    print("All tests passed!")

if __name__ == "__main__":
    test_cpu8085()