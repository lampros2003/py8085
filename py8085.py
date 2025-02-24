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
    """CPU8085 class to emulate an 8085 CPU using the DLL functions for memory and registers."""
    def __init__(self):
        # Initialize the CPU via the DLL functions (they work on global memory/registers for now)
        self.set_PC(0)
        self.set_SP(0xF000)
        self.set_flags(0)

    def fetch_instruction(self)->int:
        """Fetch the next instruction from memory and return it."""
        byte = memory_dll.read_memory(c_uint16(self.get_PC()))
        self.set_PC(self.get_PC() + 1)
        return byte

    def read_memory(self, address:int)->int:
        """Read a byte from memory at the given address."""
        return memory_dll.read_memory(c_uint16(address))

    def write_memory(self, address:int, value:int):
        memory_dll.write_memory(c_uint16(address), c_uint8(value))

    def read_register(self, regname: str)->int:
        """read the value of the register
        
        Keyword arguments:
        regname -- the name of the register to read
        Return: the value of the register
        """
        
        switcher = {
            'A': 0, 'B': 1, 'C': 2, 'D': 3,
            'E': 4, 'H': 5, 'L': 6, 'M': 7
        }
        reg_num = switcher.get(regname, -1)
        if reg_num >= 0:
            return registers_dll.read_reg(c_uint8(reg_num))
        return 0

    def write_register(self, regname:str, value:int)->None:
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
            await_input = input(f"Press Enter to execute instruction {iterator} or 'q' to quit: ")
            if await_input.lower() == 'q':
                break
            running = executor_dll.execute_instruction(byref(cpu_funcs))
            
            if  running==0:
                print("HLT encountered. Stopping execution.")
                break
            if running == -1:
                print("Error encountered. Stopping execution.")
                break





