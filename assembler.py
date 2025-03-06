class assembler:
    """Assembler class to assemble 8085 assembly code into machine code. and write it to the memory of a cpu object.
    """
    
    def __init__(self):
        
        # Define the instruction set and opcode table
        #the formats available in 8085 are the following 
        #RR - Register to Register(opcode Register Register) size of 1 byte
        #RI - Register, Immediate data(opcode Register Immediate data in memory) size of 2 bytes   
        #RP - Register pair, 16-bit data (opcode Register pair 16-bit data in memory) size of 3 bytes
        #A - 16-bit address (opcode 16-bit address) size of 3 bytes
        #N - No operand size 1 byte
        self.instruction_set = {
            # Data Transfer Group
            'MOV': {'size': 1, 'format': 'RR', 'code': 0x40},   # Base code 01000000
            'MVI': {'size': 2, 'format': 'RI', 'code': 0x06},   # Base code 00000110
            'LXI': {'size': 3, 'format': 'RP', 'code': 0x01},   # Base code 00000001
            'LDA': {'size': 3, 'format': 'A', 'code': 0x3A},    
            'STA': {'size': 3, 'format': 'A', 'code': 0x32},    
            'LHLD': {'size': 3, 'format': 'A', 'code': 0x2A},   
            'SHLD': {'size': 3, 'format': 'A', 'code': 0x22},   
            'LDAX': {'size': 1, 'format': 'RP', 'code': 0x0A},  # Base code, B=0x0A, D=0x1A
            'STAX': {'size': 1, 'format': 'RP', 'code': 0x02},  # Base code, B=0x02, D=0x12
            'XCHG': {'size': 1, 'format': 'N', 'code': 0xEB},   
            
            # Arithmetic Group
            'ADD': {'size': 1, 'format': 'RA', 'code': 0x80},   # Base code 10000rrr
            'ADI': {'size': 2, 'format': 'AI', 'code': 0xC6},  
            'ADC': {'size': 1, 'format': 'RA', 'code': 0x88},   # Base code 10001rrr
            'ACI': {'size': 2, 'format': 'AI', 'code': 0xCE},  
            'SUB': {'size': 1, 'format': 'RA', 'code': 0x90},   # Base code 10010rrr
            'SUI': {'size': 2, 'format': 'AI', 'code': 0xD6},  
            'SBB': {'size': 1, 'format': 'RA', 'code': 0x98},   # Base code 10011rrr
            'SBI': {'size': 2, 'format': 'AI', 'code': 0xDE},  
            'INR': {'size': 1, 'format': 'RA', 'code': 0x04},   # Base code 00rrRA00
            'DCR': {'size': 1, 'format': 'RA', 'code': 0x05},   # Base code 00rrRA01
            'INX': {'size': 1, 'format': 'RP', 'code': 0x03},   # Base code 00rp0011
            'DCX': {'size': 1, 'format': 'RP', 'code': 0x0B},   # Base code 00rp1011
            'DAD': {'size': 1, 'format': 'RP', 'code': 0x09},   # Base code 00rp1001
            'DAA': {'size': 1, 'format': 'N', 'code': 0x27},    
            
            # Logical Group
            'ANA': {'size': 1, 'format': 'RA', 'code': 0xA0},   # Base code 10100rrr
            'ANI': {'size': 2, 'format': 'AI', 'code': 0xE6},  
            'ORA': {'size': 1, 'format': 'RA', 'code': 0xB0},   # Base code 10110rrr
            'ORI': {'size': 2, 'format': 'AI', 'code': 0xF6},  
            'XRA': {'size': 1, 'format': 'RA', 'code': 0xA8},   # Base code 10101rrr
            'XRI': {'size': 2, 'format': 'AI', 'code': 0xEE},  
            'CMP': {'size': 1, 'format': 'RA', 'code': 0xB8},   # Base code 10111rrr
            'CPI': {'size': 2, 'format': 'AI', 'code': 0xFE},  
            'RLC': {'size': 1, 'format': 'N', 'code': 0x07},    
            'RRC': {'size': 1, 'format': 'N', 'code': 0x0F},    
            'RAL': {'size': 1, 'format': 'N', 'code': 0x17},    
            'RAR': {'size': 1, 'format': 'N', 'code': 0x1F},    
            'CMA': {'size': 1, 'format': 'N', 'code': 0x2F},    
            'CMC': {'size': 1, 'format': 'N', 'code': 0x3F},    
            'STC': {'size': 1, 'format': 'N', 'code': 0x37},    
            
            # Branch Group
            'JMP': {'size': 3, 'format': 'A', 'code': 0xC3},    
            'JZ': {'size': 3, 'format': 'A', 'code': 0xCA},     
            'JNZ': {'size': 3, 'format': 'A', 'code': 0xC2},    
            'JC': {'size': 3, 'format': 'A', 'code': 0xDA},     
            'JNC': {'size': 3, 'format': 'A', 'code': 0xD2},    
            'JP': {'size': 3, 'format': 'A', 'code': 0xF2},     
            'JM': {'size': 3, 'format': 'A', 'code': 0xFA},     
            'JPE': {'size': 3, 'format': 'A', 'code': 0xEA},    
            'JPO': {'size': 3, 'format': 'A', 'code': 0xE2},    
            'CALL': {'size': 3, 'format': 'A', 'code': 0xCD},   
            'CZ': {'size': 3, 'format': 'A', 'code': 0xCC},     
            'CNZ': {'size': 3, 'format': 'A', 'code': 0xC4},    
            'CC': {'size': 3, 'format': 'A', 'code': 0xDC},     
            'CNC': {'size': 3, 'format': 'A', 'code': 0xD4},    
            'CP': {'size': 3, 'format': 'A', 'code': 0xF4},     
            'CM': {'size': 3, 'format': 'A', 'code': 0xFC},     
            'CPE': {'size': 3, 'format': 'A', 'code': 0xEC},    
            'CPO': {'size': 3, 'format': 'A', 'code': 0xE4},    
            'RET': {'size': 1, 'format': 'N', 'code': 0xC9},    
            'RZ': {'size': 1, 'format': 'N', 'code': 0xC8},     
            'RNZ': {'size': 1, 'format': 'N', 'code': 0xC0},    
            'RC': {'size': 1, 'format': 'N', 'code': 0xD8},     
            'RNC': {'size': 1, 'format': 'N', 'code': 0xD0},    
            'RP': {'size': 1, 'format': 'N', 'code': 0xF0},     
            'RM': {'size': 1, 'format': 'N', 'code': 0xF8},     
            'RPE': {'size': 1, 'format': 'N', 'code': 0xE8},    
            'RPO': {'size': 1, 'format': 'N', 'code': 0xE0},    
            'PCHL': {'size': 1, 'format': 'N', 'code': 0xE9},   
            'RST': {'size': 1, 'format': 'RST', 'code': 0xC7},  # Base code 11nnn111
            
            # Stack, I/O, and Machine Control Group
            'PUSH': {'size': 1, 'format': 'RP', 'code': 0xC5},  # Base code 11rp0101
            'POP': {'size': 1, 'format': 'RP', 'code': 0xC1},   # Base code 11rp0001
            'XTHL': {'size': 1, 'format': 'N', 'code': 0xE3},   
            'SPHL': {'size': 1, 'format': 'N', 'code': 0xF9},   
            'IN': {'size': 2, 'format': 'IO', 'code': 0xDB},    
            'OUT': {'size': 2, 'format': 'IO', 'code': 0xD3},   
            'EI': {'size': 1, 'format': 'N', 'code': 0xFB},     
            'DI': {'size': 1, 'format': 'N', 'code': 0xF3},     
            'HLT': {'size': 1, 'format': 'N', 'code': 0x76},    
            'NOP': {'size': 1, 'format': 'N', 'code': 0x00},    
            'RIM': {'size': 1, 'format': 'N', 'code': 0x20},    
            'SIM': {'size': 1, 'format': 'N', 'code': 0x30},    
        }
            
        self.register_codes = {
            'A': 0b111, 'B': 0b000, 'C': 0b001,
            'D': 0b010, 'E': 0b011, 'H': 0b100,
            'L': 0b101, 'M': 0b110
        }
        # Define the opcode table
        # The opcode table is a dictionary with keys as tuples of the form (mnemonic, operand1, operand2) 
        # values as the opcode in machine code
        
        
    #parse the line and return the parts of the line
    #remove comments and strip whitespace
    def parse_line(self, line):
        """Parse the line and return the parts of the line which represent usefull code
        Keyword arguments: the line to parse
        Return: the parts of the line whivh represent usefull code

        """
        # Remove comments and strip whitespace
        line = line.split(';')[0].strip().upper()
        if not line:
            return None            
        # Split into parts
        parts = [p.strip() for p in line.split()]
        return parts
    #get the opcode for the given mnemonic and operands
    def get_opcode(self, mnemonic: str, dest=None, src=None) -> int:
        """Get the opcode for the given mnemonic and operands.
        
        Keyword arguments:
        mnemonic -- the mnemonic of the instruction
        dest -- the destination register (default None)
        src -- the source register (default None)
        Return: the opcode in machine code
        """
        if mnemonic not in self.instruction_set:
            return None
            
        instruction = self.instruction_set[mnemonic]
        base_code = instruction['code']
        
        if instruction['format'] == 'N':
            # No operand instructions (e.g., HLT, RET)
            return base_code
        elif instruction['format'] == 'RR':
            # Register to Register (e.g., MOV)
            return base_code | (self.register_codes[dest] << 3) | self.register_codes[src]
        elif instruction['format'] == 'RI':
            # Register, Immediate (e.g., MVI)
            return base_code | (self.register_codes[dest] << 3)
        elif instruction['format'] == 'RP':
            # Register pair operations
            rp_codes = {'B': 0, 'D': 1, 'H': 2, 'SP': 3, 'PSW': 3}
            return base_code | (rp_codes[dest] << 4)
        elif instruction['format'] == 'RA':
            # Accumulator and register operations (e.g., ADD, SUB)
            return base_code | self.register_codes[src]
        elif instruction['format'] == 'AI':
            # Accumulator and immediate operations (e.g., ADI, SUI)
            return base_code
        elif instruction['format'] == 'RST':
            # RST instruction
            return base_code | ((int(dest) & 0x07) << 3)
        elif instruction['format'] == 'IO':
            # IN/OUT instructions
            return base_code
        else:
            # Address format (e.g. JMP, CALL)
            return base_code
    
    # the actual assambling of the code into machine code
    def assemble(self, filename:str, start_address:int, cpu)->int:
        """ Assemble the given file into machine code and write to memory associated with a given cpu object.
        Keyword arguments:
        filename -- the name of the file to assemble
        start_address -- the address to start writing the machine code
        cpu -- the CPU object whose memory will be written
        
        Return: number of bytes written to memory
        """
        
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
                    
                    inst_format = self.instruction_set[mnemonic]['format']
                    inst_size = self.instruction_set[mnemonic]['size']
                    
                    # No operand instructions (e.g., HLT, RET)
                    if inst_format == 'N':
                        opcode = self.get_opcode(mnemonic)
                        cpu.write_memory(current_address, opcode)
                        current_address += 1
                        
                    # Register to Register instructions (e.g., MOV)
                    elif inst_format == 'RR':
                        if len(parts) != 3:
                            raise SyntaxError(f"Invalid operands for {mnemonic} at line {line_num}")
                        dest, src = parts[1].strip(','), parts[2]
                        opcode = self.get_opcode(mnemonic, dest, src)
                        cpu.write_memory(current_address, opcode)
                        current_address += 1
                        
                    # Register with immediate value (e.g., MVI)
                    elif inst_format == 'RI':
                        if len(parts) != 3:
                            raise SyntaxError(f"Invalid operands for {mnemonic} at line {line_num}")
                        dest = parts[1].strip(',')
                        imm = self._parse_number(parts[2])
                        opcode = self.get_opcode(mnemonic, dest)
                        cpu.write_memory(current_address, opcode)
                        cpu.write_memory(current_address + 1, imm)
                        current_address += 2
                        
                    # Register pair operations (e.g., LXI)
                    elif inst_format == 'RP':
                        if mnemonic in ['LXI']:
                            if len(parts) != 3:
                                raise SyntaxError(f"Invalid operands for {mnemonic} at line {line_num}")
                            dest = parts[1].strip(',')
                            imm = self._parse_number(parts[2])
                            opcode = self.get_opcode(mnemonic, dest)
                            cpu.write_memory(current_address, opcode)
                            cpu.write_memory(current_address + 1, imm & 0xFF)
                            cpu.write_memory(current_address + 2, (imm >> 8) & 0xFF)
                            current_address += 3
                        else:  # PUSH, POP, INX, DCX, DAD
                            if len(parts) != 2:
                                raise SyntaxError(f"Invalid operands for {mnemonic} at line {line_num}")
                            dest = parts[1]
                            opcode = self.get_opcode(mnemonic, dest)
                            cpu.write_memory(current_address, opcode)
                            current_address += 1
                        
                    # Address-based instructions (e.g., JMP, LDA)
                    elif inst_format == 'A':
                        if len(parts) != 2:
                            raise SyntaxError(f"Invalid operands for {mnemonic} at line {line_num}")
                        addr = self._parse_number(parts[1])
                        opcode = self.get_opcode(mnemonic)
                        cpu.write_memory(current_address, opcode)
                        cpu.write_memory(current_address + 1, addr & 0xFF)
                        cpu.write_memory(current_address + 2, (addr >> 8) & 0xFF)
                        current_address += 3
                        
                    # Accumulator operations (e.g., ADD A)
                    elif inst_format == 'RA':
                        if len(parts) != 2:
                            raise SyntaxError(f"Invalid operands for {mnemonic} at line {line_num}")
                        src = parts[1]
                        opcode = self.get_opcode(mnemonic, src=src)
                        cpu.write_memory(current_address, opcode)
                        current_address += 1
                        
                    # Accumulator with immediate (e.g., ADI)
                    elif inst_format == 'AI':
                        if len(parts) != 2:
                            raise SyntaxError(f"Invalid operands for {mnemonic} at line {line_num}")
                        imm = self._parse_number(parts[1])
                        opcode = self.get_opcode(mnemonic)
                        cpu.write_memory(current_address, opcode)
                        cpu.write_memory(current_address + 1, imm)
                        current_address += 2
                        
                    # RST instructions
                    elif inst_format == 'RST':
                        if len(parts) != 2:
                            raise SyntaxError(f"Invalid operands for {mnemonic} at line {line_num}")
                        vec = int(parts[1])
                        if not 0 <= vec <= 7:
                            raise ValueError(f"RST vector must be between 0-7, got {vec}")
                        opcode = self.get_opcode(mnemonic, dest=str(vec))
                        cpu.write_memory(current_address, opcode)
                        current_address += 1
                        
                    # I/O instructions (IN, OUT)
                    elif inst_format == 'IO':
                        if len(parts) != 2:
                            raise SyntaxError(f"Invalid operands for {mnemonic} at line {line_num}")
                        port = self._parse_number(parts[1])
                        opcode = self.get_opcode(mnemonic)
                        cpu.write_memory(current_address, opcode)
                        cpu.write_memory(current_address + 1, port)
                        current_address += 2

            return current_address - start_address  # Return number of bytes written
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            return 0
        except Exception as e:
            print(f"Error at line {line_num}: {str(e)}")
            return 0

    def _parse_number(self, value_str):
        """Parse a number from string, supporting hex (with H suffix) and decimal."""
        value_str = value_str.strip()
        if value_str.upper().endswith('H'):
            return int(value_str[:-1], 16)
        else:
            return int(value_str)