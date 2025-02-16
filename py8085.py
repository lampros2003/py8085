import sys
import os
import ctypes
import platform

print(f"Python architecture: {platform.architecture()[0]}")

# Load the shared libraries
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    memaccess = ctypes.CDLL(os.path.join(current_dir, 'memory.dll'))
    regaccess = ctypes.CDLL(os.path.join(current_dir, 'registers.dll'))
except Exception as e:
    print(f"Error loading DLLs: {e}")
    sys.exit(1)

# Define function prototypes for memory access
memaccess.read_memory.argtypes = [ctypes.c_uint16]
memaccess.read_memory.restype = ctypes.c_uint8
memaccess.write_memory.argtypes = [ctypes.c_uint16, ctypes.c_uint8]
memaccess.write_memory.restype = None

# Define function prototypes for register access
regaccess.read_reg.argtypes = [ctypes.c_uint8]
regaccess.read_reg.restype = ctypes.c_uint8
regaccess.write_reg.argtypes = [ctypes.c_uint8, ctypes.c_uint8]
regaccess.write_reg.restype = None
regaccess.get_flags.argtypes = []
regaccess.get_flags.restype = ctypes.c_uint8
regaccess.set_flags.argtypes = [ctypes.c_uint8]
regaccess.set_flags.restype = None
regaccess.get_PC.argtypes = []
regaccess.get_PC.restype = ctypes.c_uint16
regaccess.set_PC.argtypes = [ctypes.c_uint16]
regaccess.set_PC.restype = None
regaccess.get_SP.argtypes = []
regaccess.get_SP.restype = ctypes.c_uint16
regaccess.set_SP.argtypes = [ctypes.c_uint16]
regaccess.set_SP.restype = None

class CPU8085:
    def __init__(self):
        self.PC = 0
        self.set_PC(0)
        self.set_SP(0xF000)
        self.set_flags(0)

    def fetch_instruction(self):
        byte = memaccess.read_memory(ctypes.c_uint16(self.get_PC()))
        self.set_PC(self.get_PC() + 1)
        return byte

    def read_memory(self, address):
        return memaccess.read_memory(ctypes.c_uint16(address))

    def write_memory(self, address, value):
        memaccess.write_memory(ctypes.c_uint16(address), ctypes.c_uint8(value))

    def read_register(self, regname):
        switcher = {
            'A': 0, 'B': 1, 'C': 2, 'D': 3,
            'E': 4, 'H': 5, 'L': 6, 'M': 7
        }
        reg_num = switcher.get(regname, -1)
        if reg_num >= 0:
            return regaccess.read_reg(ctypes.c_uint8(reg_num))
        return 0

    def write_register(self, regname, value):
        switcher = {
            'A': 0, 'B': 1, 'C': 2, 'D': 3,
            'E': 4, 'H': 5, 'L': 6, 'M': 7
        }
        reg_num = switcher.get(regname, -1)
        if reg_num >= 0:
            regaccess.write_reg(ctypes.c_uint8(reg_num), ctypes.c_uint8(value))

    def get_flags(self):
        return regaccess.get_flags()

    def set_flags(self, value):
        regaccess.set_flags(ctypes.c_uint8(value))

    def get_PC(self):
        return regaccess.get_PC()

    def set_PC(self, value):
        regaccess.set_PC(ctypes.c_uint16(value))

    def get_SP(self):
        return regaccess.get_SP()

    def set_SP(self, value):
        regaccess.set_SP(ctypes.c_uint16(value))

    def run(self):
        while True:
            opcode = self.fetch_instruction()
            print(f"Opcode: {opcode}")
            if opcode == 0x76:
                break


class assembler:
    def __init__(self):
        self.instruction_set = {
            'MOV': {'size': 1, 'format': 'RR'},  # Register to Register
            'MVI': {'size': 2, 'format': 'RI'},  # Register, Immediate data
            'LXI': {'size': 3, 'format': 'RP'},  # Register pair, 16-bit data
            'LDA': {'size': 3, 'format': 'A'},   # 16-bit address
            'STA': {'size': 3, 'format': 'A'},   # 16-bit address
            'HLT': {'size': 1, 'format': 'N'},   # No operands
        }
        
        self.register_codes = {
            'A': 0b111, 'B': 0b000, 'C': 0b001,
            'D': 0b010, 'E': 0b011, 'H': 0b100,
            'L': 0b101, 'M': 0b110
        }
        
        self.opcode_table = {
            ('MOV', 'R', 'R'): 0b01000000,  # 0x40
            ('MVI', 'R', 'I'): 0b00000110,  # 0x06
            'HLT': 0x76,
            'LDA': 0x3A,
            'STA': 0x32,
        }

    def parse_line(self, line):
        # Remove comments and strip whitespace
        line = line.split(';')[0].strip().upper()
        if not line:
            return None
            
        # Split into parts
        parts = [p.strip() for p in line.split()]
        return parts

    def get_opcode(self, mnemonic, dest=None, src=None):
        if mnemonic == 'MOV':
            base = self.opcode_table[('MOV', 'R', 'R')]
            dest_code = self.register_codes[dest] << 3
            src_code = self.register_codes[src]
            return base | dest_code | src_code
        elif mnemonic == 'MVI':
            base = self.opcode_table[('MVI', 'R', 'I')]
            dest_code = self.register_codes[dest] << 3
            return base | dest_code
        return self.opcode_table.get(mnemonic, None)

    def assemble(self, filename, start_address):
        current_address = start_address
        memory_writer = CPU8085()  # Create instance to access memory functions
        
        try:
            with open(filename, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    parts = self.parse_line(line)
                    if not parts:
                        continue
                        
                    mnemonic = parts[0]
                    if mnemonic not in self.instruction_set:
                        raise SyntaxError(f"Invalid instruction '{mnemonic}' at line {line_num}")

                    inst_format = self.instruction_set[mnemonic]
                    
                    # Handle different instruction formats
                    if inst_format['format'] == 'N':  # No operands (HLT)
                        opcode = self.get_opcode(mnemonic)
                        memory_writer.write_memory(current_address, opcode)
                        current_address += 1
                        
                    elif inst_format['format'] == 'RR':  # Register to Register
                        if len(parts) != 3:
                            raise SyntaxError(f"Invalid operands for {mnemonic} at line {line_num}")
                        dest, src = parts[1].strip(','), parts[2]
                        opcode = self.get_opcode(mnemonic, dest, src)
                        memory_writer.write_memory(current_address, opcode)
                        current_address += 1
                        
                    elif inst_format['format'] == 'RI':  # Register, Immediate
                        if len(parts) != 3:
                            raise SyntaxError(f"Invalid operands for {mnemonic} at line {line_num}")
                        dest = parts[1].strip(',')
                        imm = int(parts[2].strip('H'), 16) if parts[2].endswith('H') else int(parts[2])
                        opcode = self.get_opcode(mnemonic, dest)
                        memory_writer.write_memory(current_address, opcode)
                        memory_writer.write_memory(current_address + 1, imm)
                        current_address += 2
                        
                    elif inst_format['format'] == 'A':  # Address
                        if len(parts) != 2:
                            raise SyntaxError(f"Invalid operands for {mnemonic} at line {line_num}")
                        addr = int(parts[1].strip('H'), 16) if parts[1].endswith('H') else int(parts[1])
                        opcode = self.get_opcode(mnemonic)
                        memory_writer.write_memory(current_address, opcode)
                        memory_writer.write_memory(current_address + 1, addr & 0xFF)
                        memory_writer.write_memory(current_address + 2, (addr >> 8) & 0xFF)
                        current_address += 3

            return current_address - start_address  # Return number of bytes assembled
            
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            return 0
        except Exception as e:
            print(f"Error at line {line_num}: {str(e)}")
            return 0    



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
def test_assembler():
    # Create a test assembly file
    with open('test.asm', 'w') as f:
        f.write("""
        MVI A, 42H    ; Load 42H into A
        MOV B, A      ; Copy A to B
        STA 2000H     ; Store A at memory location 2000H
        HLT           ; Stop
        """)

    # Create and run assembler
    asm = assembler()
    bytes_assembled = asm.assemble('test.asm', 0x1000)
    
    # Create CPU instance to verify memory contents
    cpu = CPU8085()
    
    # Verify assembled code
    assert bytes_assembled > 0, "Assembly failed"
    assert cpu.read_memory(0x1000) == 0x3E, "MVI A opcode incorrect"
    assert cpu.read_memory(0x1001) == 0x42, "Immediate value incorrect"
    assert cpu.read_memory(0x1002) == 0x47, "MOV B,A opcode incorrect"
    assert cpu.read_memory(0x1003) == 0x32, "STA opcode incorrect"
    assert cpu.read_memory(0x1006) == 0x76, "HLT opcode incorrect"
    
    print("Assembler tests passed!")

if __name__ == "__main__":
    test_assembler()
    test_cpu8085()