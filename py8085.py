from ctypes import *
import os

class CPU8085Functions(Structure):
    """Structure holding function pointers for the CPU executor."""
    _fields_ = [
        ("read_memory", CFUNCTYPE(c_uint8, c_uint16)),
        ("write_memory", CFUNCTYPE(None, c_uint16, c_uint8)),
        ("read_reg", CFUNCTYPE(c_uint8, c_uint8)),
        ("write_reg", CFUNCTYPE(None, c_uint8, c_uint8)),
        ("get_flags", CFUNCTYPE(c_uint8)),
        ("set_flags", CFUNCTYPE(None, c_uint8)),
        ("get_pc", CFUNCTYPE(c_uint16)),
        ("set_pc", CFUNCTYPE(None, c_uint16)),
        ("get_sp", CFUNCTYPE(c_uint16)),
        ("set_sp", CFUNCTYPE(None, c_uint16))
    ]

class Memory:
    """Wrapper for the memory DLL functions."""
    
    def __init__(self, dll_name='memory.dll'):
        """
        Initialize a Memory object.

        Keyword arguments:
        dll_name -- name of the Memory DLL file (default: 'memory.dll')

        Return: None
        """
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.dll = CDLL(os.path.join(current_dir, dll_name))
            
            # Configure DLL functions
            self.dll.create_memory.restype = c_void_p
            self.dll.destroy_memory.argtypes = [c_void_p]
            self.dll.read_memory.argtypes = [c_void_p, c_uint16]
            self.dll.read_memory.restype = c_uint8
            self.dll.write_memory.argtypes = [c_void_p, c_uint16, c_uint8]
            
            self.handle = self.dll.create_memory()
        except Exception as e:
            print(f"Error loading Memory DLL '{dll_name}': {e}")
            raise
        
    def __del__(self):
        """Destructor for Memory object."""
        self.dll.destroy_memory(self.handle)
        
    def read(self, address):
        """Read a single byte from memory."""
        return self.dll.read_memory(self.handle, c_uint16(address))
        
    def write(self, address, value):
        """Write a single byte to memory."""
        self.dll.write_memory(self.handle, c_uint16(address), c_uint8(value))

class Registers:
    """Wrapper for the registers DLL functions."""
    
    REG_MAP = {
        'A': 0, 'B': 1, 'C': 2, 'D': 3,
        'E': 4, 'H': 5, 'L': 6, 'M': 7
    }
    
    def __init__(self, dll_name='registers.dll'):
        """
        Initialize a Registers object.

        Keyword arguments:
        dll_name -- name of the Registers DLL file (default: 'registers.dll')

        Return: None
        """
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.dll = CDLL(os.path.join(current_dir, dll_name))
            
            # Configure DLL functions
            self.dll.create_registers.restype = c_void_p
            self.dll.destroy_registers.argtypes = [c_void_p]
            self.dll.read_reg.argtypes = [c_void_p, c_uint8]
            self.dll.read_reg.restype = c_uint8
            self.dll.write_reg.argtypes = [c_void_p, c_uint8, c_uint8]
            self.dll.get_flags.argtypes = [c_void_p]
            self.dll.get_flags.restype = c_uint8
            self.dll.set_flags.argtypes = [c_void_p, c_uint8]
            self.dll.get_PC.argtypes = [c_void_p]
            self.dll.get_PC.restype = c_uint16
            self.dll.set_PC.argtypes = [c_void_p, c_uint16]
            self.dll.get_SP.argtypes = [c_void_p]
            self.dll.get_SP.restype = c_uint16
            self.dll.set_SP.argtypes = [c_void_p, c_uint16]
            
            self.handle = self.dll.create_registers()
        except Exception as e:
            print(f"Error loading Registers DLL '{dll_name}': {e}")
            raise
        
    def __del__(self):
        """Destructor for Registers object."""
        self.dll.destroy_registers(self.handle)
        
    def read_reg(self, regname):
        """Read the value from a register."""
        reg_num = self.REG_MAP.get(regname, -1)
        if reg_num >= 0:
            return self.dll.read_reg(self.handle, c_uint8(reg_num))
        return 0
        
    def write_reg(self, regname, value):
        """Write a value to a register."""
        reg_num = self.REG_MAP.get(regname, -1)
        if reg_num >= 0:
            self.dll.write_reg(self.handle, c_uint8(reg_num), c_uint8(value))
            
    def get_flags(self):
        """Get the flags register."""
        return self.dll.get_flags(self.handle)
        
    def set_flags(self, value):
        """Set the flags register."""
        self.dll.set_flags(self.handle, c_uint8(value))
        
    def get_PC(self):
        """Get the value of the program counter."""
        return self.dll.get_PC(self.handle)
        
    def set_PC(self, value):
        """Set the value of the program counter."""
        self.dll.set_PC(self.handle, c_uint16(value))
        
    def get_SP(self):
        """Get the value of the stack pointer."""
        return self.dll.get_SP(self.handle)
        
    def set_SP(self, value):
        """Set the value of the stack pointer."""
        self.dll.set_SP(self.handle, c_uint16(value))

class Executor:
    """Wrapper for the executor DLL functions."""
    
    def __init__(self, cpu, dll_name='executor.dll'):
        """
        Initialize an Executor object.

        Keyword arguments:
        cpu -- CPU8085 object to link the executor with
        dll_name -- name of the Executor DLL file (default: 'executor.dll')

        Return: None
        """
        self.cpu = cpu
        
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.dll = CDLL(os.path.join(current_dir, dll_name))
            
            # Configure DLL functions
            self.dll.execute_instruction.argtypes = [POINTER(CPU8085Functions)]
            self.dll.execute_instruction.restype = c_int
        except Exception as e:
            print(f"Error loading Executor DLL '{dll_name}': {e}")
            raise
            
        self.cpu_funcs = self._setup_cpu_functions()
        
    def _setup_cpu_functions(self):
        """Setup the CPU8085Functions structure with Python callbacks."""
        cpu_funcs = CPU8085Functions()
        
        @CFUNCTYPE(c_uint8, c_uint16)
        def read_memory_cb(address):
            return self.cpu.read_memory(address)
            
        @CFUNCTYPE(None, c_uint16, c_uint8)
        def write_memory_cb(address, value):
            self.cpu.write_memory(address, value)
            
        @CFUNCTYPE(c_uint8, c_uint8)
        def read_reg_cb(reg):
            reg_names = ['B', 'C', 'D', 'E', 'H', 'L', 'M', 'A']
            if reg < len(reg_names):
                return self.cpu.read_register(reg_names[reg])
            return 0
            
        @CFUNCTYPE(None, c_uint8, c_uint8)
        def write_reg_cb(reg, value):
            reg_names = ['B', 'C', 'D', 'E', 'H', 'L', 'M', 'A']
            if reg < len(reg_names):
                self.cpu.write_register(reg_names[reg], value)
                
        @CFUNCTYPE(c_uint8)
        def get_flags_cb():
            return self.cpu.get_flags()
            
        @CFUNCTYPE(None, c_uint8)
        def set_flags_cb(value):
            self.cpu.set_flags(value)
            
        @CFUNCTYPE(c_uint16)
        def get_pc_cb():
            return self.cpu.get_PC()
            
        @CFUNCTYPE(None, c_uint16)
        def set_pc_cb(value):
            self.cpu.set_PC(value)
            
        @CFUNCTYPE(c_uint16)
        def get_sp_cb():
            return self.cpu.get_SP()
            
        @CFUNCTYPE(None, c_uint16)
        def set_sp_cb(value):
            self.cpu.set_SP(value)

        cpu_funcs.read_memory = read_memory_cb
        cpu_funcs.write_memory = write_memory_cb
        cpu_funcs.read_reg = read_reg_cb
        cpu_funcs.write_reg = write_reg_cb
        cpu_funcs.get_flags = get_flags_cb
        cpu_funcs.set_flags = set_flags_cb
        cpu_funcs.get_pc = get_pc_cb
        cpu_funcs.set_pc = set_pc_cb
        cpu_funcs.get_sp = get_sp_cb
        cpu_funcs.set_sp = set_sp_cb
        
        return cpu_funcs

    def execute_instruction(self):
        """Execute a single instruction using the linked CPU8085Functions."""
        return self.dll.execute_instruction(byref(self.cpu_funcs))

class CPU8085:
    """CPU8085 class to emulate an 8085 CPU."""
    
    def __init__(self, memory=None, registers=None, 
                 memory_dll='memory.dll', registers_dll='registers.dll', executor_dll='executor.dll'):
        """
        Construct a CPU8085 object.

        Keyword arguments:
        memory -- Memory object to use for memory operations (default None)
        registers -- Registers object to use for register operations (default None)
        memory_dll -- Name of the Memory DLL file if memory is None (default: 'memory.dll')
        registers_dll -- Name of the Registers DLL file if registers is None (default: 'registers.dll')
        executor_dll -- Name of the Executor DLL file (default: 'executor.dll')

        Return: CPU8085 object
        """
        self.memory = memory if memory else Memory(dll_name=memory_dll)
        self.registers = registers if registers else Registers(dll_name=registers_dll)
        self.executor = Executor(self, dll_name=executor_dll)
        
        self.set_PC(0)
        self.set_SP(0xF000)
        self.set_flags(0)

    def fetch_instruction(self):
        """
        Fetch the next instruction from memory.

        Keyword arguments:
        None --

        Return: the byte of the fetched instruction (int)
        """
        byte = self.read_memory(self.get_PC())
        self.set_PC(self.get_PC() + 1)
        return byte

    def read_memory(self, address):
        """
        Read a byte from memory.

        Keyword arguments:
        address -- memory address to read from (int)

        Return: the byte read (int)
        """
        return self.memory.read(address)

    def write_memory(self, address, value):
        """
        Write a byte to memory.

        Keyword arguments:
        address -- memory address to write to (int)
        value -- value to be written (int)

        Return: None
        """
        self.memory.write(address, value)

    def read_register(self, regname):
        """
        Read from a CPU register.

        Keyword arguments:
        regname -- name of the register (e.g. 'A', 'B', etc.)

        Return: contents of the register (int)
        """
        return self.registers.read_reg(regname)

    def write_register(self, regname, value):
        """
        Write a value to a CPU register.

        Keyword arguments:
        regname -- name of the register (e.g. 'A', 'B', etc.)
        value -- value to write (int)

        Return: None
        """
        self.registers.write_reg(regname, value)

    def get_flags(self):
        """
        Get the current flags register.

        Keyword arguments:
        None --

        Return: flags register (int)
        """
        return self.registers.get_flags()

    def set_flags(self, value):
        """
        Set the flags register.

        Keyword arguments:
        value -- new flags value (int)

        Return: None
        """
        self.registers.set_flags(value)

    def get_PC(self):
        """
        Get the program counter.

        Keyword arguments:
        None --

        Return: program counter (int)
        """
        return self.registers.get_PC()

    def set_PC(self, value):
        """
        Set the program counter.

        Keyword arguments:
        value -- new program counter (int)

        Return: None
        """
        self.registers.set_PC(value)

    def get_SP(self):
        """
        Get the stack pointer.

        Keyword arguments:
        None --

        Return: stack pointer (int)
        """
        return self.registers.get_SP()

    def set_SP(self, value):
        """
        Set the stack pointer.

        Keyword arguments:
        value -- new stack pointer (int)

        Return: None
        """
        self.registers.set_SP(value)

    def execute(self):
        """
        Continuously execute instructions until a HALT or quit condition.

        Keyword arguments:
        None --

        Return: None
        """
        instruction_count = 0
        while True:
            instruction_count += 1
            await_input = input(f"Press Enter to execute instruction {instruction_count} or 'q' to quit: ")
            if await_input.lower() == 'q':
                break
            result = self.executor.execute_instruction()
            if result != 1:
                print(f"Execution stopped: result code {result}")
                break

