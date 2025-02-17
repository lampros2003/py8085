import sys
import os
from ctypes import c_uint8, c_uint16, c_bool, CFUNCTYPE, POINTER, Structure, byref,CDLL
import platform

print(f"Python architecture: {platform.architecture()[0]}")

# Load the shared libraries
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    memory_dll = CDLL(os.path.join(current_dir, 'memory.dll'))
    registers_dll = CDLL(os.path.join(current_dir, 'registers.dll'))
    executor_dll = CDLL(os.path.join(current_dir, 'executor.dll'))
except Exception as e:
    print(f"Error loading DLLs: {e}")
    sys.exit(1)

# Define function prototypes for memory access
memory_dll.read_memory.argtypes = [c_uint16]
memory_dll.read_memory.restype = c_uint8
memory_dll.write_memory.argtypes = [c_uint16, c_uint8]
memory_dll.write_memory.restype = None

# Define function prototypes for register access
registers_dll.read_reg.argtypes = [c_uint8]
registers_dll.read_reg.restype = c_uint8
registers_dll.write_reg.argtypes = [c_uint8, c_uint8]
registers_dll.write_reg.restype = None
registers_dll.get_flags.argtypes = []
registers_dll.get_flags.restype = c_uint8
registers_dll.set_flags.argtypes = [c_uint8]
registers_dll.set_flags.restype = None
registers_dll.get_PC.argtypes = []
registers_dll.get_PC.restype = c_uint16
registers_dll.set_PC.argtypes = [c_uint16]
registers_dll.set_PC.restype = None
registers_dll.get_SP.argtypes = []
registers_dll.get_SP.restype = c_uint16
registers_dll.set_SP.argtypes = [c_uint16]
registers_dll.set_SP.restype = None


#pointers for executor functions
READ_MEMORY = CFUNCTYPE(c_uint8, c_uint16)
WRITE_MEMORY = CFUNCTYPE(None, c_uint16, c_uint8)
READ_REG = CFUNCTYPE(c_uint8, c_uint8)
WRITE_REG = CFUNCTYPE(None, c_uint8, c_uint8)
GET_FLAGS = CFUNCTYPE(c_uint8)
SET_FLAGS = CFUNCTYPE(None, c_uint8)
GET_PC = CFUNCTYPE(c_uint16)
SET_PC = CFUNCTYPE(None, c_uint16)
GET_SP = CFUNCTYPE(c_uint16)
SET_SP = CFUNCTYPE(None, c_uint16)


# structure to hold the cpu functions
class CPU8085Functions(Structure):
    _fields_ = [
        ("read_memory", READ_MEMORY),
        ("write_memory", WRITE_MEMORY),
        ("read_reg", READ_REG),
        ("write_reg", WRITE_REG),
        ("get_flags", GET_FLAGS),
        ("set_flags", SET_FLAGS),
        ("get_pc", GET_PC),        
        ("set_pc", SET_PC),
        ("get_sp", GET_SP),
        ("set_sp", SET_SP),
    ]

#attach the functions from our memory and register implementation python wrappers
read_memory_callback = READ_MEMORY(memory_dll.read_memory)
write_memory_callback = WRITE_MEMORY(memory_dll.write_memory)
read_reg_callback = READ_REG(registers_dll.read_reg)
write_reg_callback = WRITE_REG(registers_dll.write_reg)
get_flags_callback = GET_FLAGS(registers_dll.get_flags)
set_flags_callback = SET_FLAGS(registers_dll.set_flags)
get_pc_callback = GET_PC(registers_dll.get_PC)
set_pc_callback = SET_PC(registers_dll.set_PC)
get_sp_callback = GET_SP(registers_dll.get_SP)
set_sp_callback = SET_SP(registers_dll.set_SP)

#Create the CPU8085Functions struct to pass into executor
cpu_funcs = CPU8085Functions(
    read_memory_callback,
    write_memory_callback,
    read_reg_callback,
    write_reg_callback,
    get_flags_callback,
    set_flags_callback,
    get_pc_callback,
    set_pc_callback,
    get_sp_callback,
    set_sp_callback
)


#expose the funcitons of the executor, makeing them available in python.
executor_dll.execute_instruction.argtypes = [POINTER(CPU8085Functions)]
executor_dll.execute_instruction.restype = c_bool



class CPU8085:
    def __init__(self):
        # Initialize the CPU via the DLL functions (they work on global memory/registers for now)
        self.set_PC(0)
        self.set_SP(0xF000)
        self.set_flags(0)

    def fetch_instruction(self):
        byte = memory_dll.read_memory(c_uint16(self.get_PC()))
        self.set_PC(self.get_PC() + 1)
        return byte

    def read_memory(self, address):
        return memory_dll.read_memory(c_uint16(address))

    def write_memory(self, address, value):
        memory_dll.write_memory(c_uint16(address), c_uint8(value))

    def read_register(self, regname):
        switcher = {
            'A': 0, 'B': 1, 'C': 2, 'D': 3,
            'E': 4, 'H': 5, 'L': 6, 'M': 7
        }
        reg_num = switcher.get(regname, -1)
        if reg_num >= 0:
            return registers_dll.read_reg(c_uint8(reg_num))
        return 0

    def write_register(self, regname, value):
        switcher = {
            'A': 0, 'B': 1, 'C': 2, 'D': 3,
            'E': 4, 'H': 5, 'L': 6, 'M': 7
        }
        reg_num = switcher.get(regname, -1)
        if reg_num >= 0:
            registers_dll.write_reg(c_uint8(reg_num), c_uint8(value))

    def get_flags(self):
        return registers_dll.get_flags()

    def set_flags(self, value):
        registers_dll.set_flags(c_uint8(value))

    def get_PC(self):
        return registers_dll.get_PC()

    def set_PC(self, value):
        registers_dll.set_PC(c_uint16(value))

    def get_SP(self):
        return registers_dll.get_SP()

    def set_SP(self, value):
        registers_dll.set_SP(c_uint16(value))

    def execute(self):
        """Continuously call the executor DLL function to execute instructions
           from memory until a HLT is encountered."""
        iterator = 0
        while True:
            iterator += 1
            running = executor_dll.execute_instruction(byref(cpu_funcs))
            # Optionally, print the internal state for debugging
            print(f"Iteration: {iterator}") 
            print(f"PC: {self.get_PC()}  SP: {self.get_SP()}  Flags: {self.get_flags()}  A: {registers_dll.read_reg(0)}")
            print(memory_dll.read_memory(0x0000), memory_dll.read_memory(0x0001), memory_dll.read_memory(0x0002))
            if not running:
                print("HLT encountered. Stopping execution.")
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
            ('MOV', 'R', 'R'): 0b01000000,  # Base opcode for MOV Register,Register
            ('MVI', 'R', 'I'): 0b00000110,  # Base for MVI Register,Immediate
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

    def assemble(self, filename, start_address, cpu):
        current_address = start_address
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
                    
                    # No operand instructions (e.g., HLT)
                    if inst_format['format'] == 'N':
                        opcode = self.get_opcode(mnemonic)
                        cpu.write_memory(current_address, opcode)
                        current_address += 1
                    # Two-register instructions (e.g., MOV)
                    elif inst_format['format'] == 'RR':
                        if len(parts) != 3:
                            raise SyntaxError(f"Invalid operands for {mnemonic} at line {line_num}")
                        dest, src = parts[1].strip(','), parts[2]
                        opcode = self.get_opcode(mnemonic, dest, src)
                        cpu.write_memory(current_address, opcode)
                        current_address += 1
                    # Register with immediate value (e.g., MVI)
                    elif inst_format['format'] == 'RI':
                        if len(parts) != 3:
                            raise SyntaxError(f"Invalid operands for {mnemonic} at line {line_num}")
                        dest = parts[1].strip(',')
                        imm = int(parts[2].strip('H'), 16) if parts[2].endswith('H') else int(parts[2])
                        opcode = self.get_opcode(mnemonic, dest)
                        cpu.write_memory(current_address, opcode)
                        cpu.write_memory(current_address + 1, imm)
                        current_address += 2
                    # Address-based instructions (e.g., LDA, STA)
                    elif inst_format['format'] == 'A':
                        if len(parts) != 2:
                            raise SyntaxError(f"Invalid operands for {mnemonic} at line {line_num}")
                        addr = int(parts[1].strip('H'), 16) if parts[1].endswith('H') else int(parts[1])
                        opcode = self.get_opcode(mnemonic)
                        cpu.write_memory(current_address, opcode)
                        cpu.write_memory(current_address + 1, addr & 0xFF)
                        cpu.write_memory(current_address + 2, (addr >> 8) & 0xFF)
                        current_address += 3

            return current_address - start_address  # Return number of bytes written
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            return 0
        except Exception as e:
            print(f"Error at line {line_num}: {str(e)}")
            return 0



if __name__ == "__main__":
    # Run assembler (assemble code into global memory)
    asm = assembler()
    test_cpu = CPU8085()
    assembled_bytes = asm.assemble('test.asm', 0x0000, cpu=test_cpu)
    print(f"Total {assembled_bytes} bytes assembled.")

    # Create a CPU instance and execute instructions from memory
    
    test_cpu.execute()  # This calls executor_dll.execute_instruction repeatedly