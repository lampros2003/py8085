##8085 emulator
import sys
import os
import time
import re
import random
# memory_interface.py
import ctypes

# Load the shared library
memaccess = ctypes.CDLL('./memory.so')
regaccess = ctypes.CDLL('./registers.so')

# Define function prototypes
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
    # Fetch insruction from memory
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
            opcode = self.fetch_byte()
            print(f"Opcode: {opcode}")
            if opcode == 0x76:
                break