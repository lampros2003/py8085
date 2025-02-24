
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
        self.instruction_set = {
            'MOV': {'size': 1, 'format': 'RR'},   # Register to Register
            'MVI': {'size': 2, 'format': 'RI'},   # Register, Immediate data
            'LXI': {'size': 3, 'format': 'RP'},   # Register pair, 16-bit data
            'LDA': {'size': 3, 'format': 'A'},    # 16-bit address
            'STA': {'size': 3, 'format': 'A'},    # 16-bit address
            'HLT': {'size': 1, 'format': 'N'},    # No operands
            'ADD': {'size': 1, 'format': 'R1'},   # One register operand (added to accumulator)
            'ADI': {'size': 2, 'format': 'RI1'},  # Immediate addition to accumulator
            'SUB': {'size': 1, 'format': 'R1'},   # One register operand subtraction (from accumulator)
            'SUI': {'size': 2, 'format': 'RI1'},  # Immediate subtraction from accumulator
        }
            
        self.register_codes = {
            'A': 0b111, 'B': 0b000, 'C': 0b001,
            'D': 0b010, 'E': 0b011, 'H': 0b100,
            'L': 0b101, 'M': 0b110
        }
        # Define the opcode table
        # The opcode table is a dictionary with keys as tuples of the form (mnemonic, operand1, operand2) 
        # values as the opcode in machine code
        
        self.opcode_table = {
            ('MOV', 'R', 'R'): 0b01000000,   # Base opcode for MOV Register,Register
            ('MVI', 'R', 'I'): 0b00000110,   # Base for MVI Register,Immediate
            ('LXI', 'RP'): 0x01,             # Base opcode for LXI RegisterPair,Immediate
            'HLT': 0x76,
            'LDA': 0x3A,
            'STA': 0x32,
            'ADD': 0x80,                   # Base opcode for ADD; register code will be OR'ed in
            'ADI': 0xC6,
            'SUB': 0x90,                   # Base opcode for SUB; register code will be OR'ed in
            'SUI': 0xD6,
        }
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
        dest -- the destination  (default None)
        src -- the source  (default None)
        Return: the opcode in machine code
        """
        if mnemonic == 'MOV':
            base = self.opcode_table[('MOV', 'R', 'R')]
            dest_code = self.register_codes[dest] << 3
            src_code = self.register_codes[src]
            return base | dest_code | src_code
        elif mnemonic == 'MVI':
            base = self.opcode_table[('MVI', 'R', 'I')]
            dest_code = self.register_codes[dest] << 3
            return base | dest_code
        elif mnemonic == 'ADD':
            # ADD r: opcode = 0x80 OR register code.
            # Note: The destination (accumulator) is implicit.
            return self.opcode_table['ADD'] | self.register_codes[src]
        elif mnemonic == 'ADI':
            # Immediate addition: opcode is fixed.
            return self.opcode_table['ADI']
        elif mnemonic == 'SUB':
            # SUB r: opcode = 0x90 OR register code.
            return self.opcode_table['SUB'] | self.register_codes[src]
        elif mnemonic == 'SUI':
            # Immediate subtraction: opcode is fixed.
            return self.opcode_table['SUI']
        else:
           
            return self.opcode_table.get(mnemonic, None)
    
    # the actual assambling of the code into machine code
    def assemble(self, filename:str, start_address:int, cpu)->int:
        """ Assemble the given file into machine code and write to memory associated with a given cpu object.
        Keyword arguments:
        filename -- the name of the file to assemble
        start_address -- the address to start writing the machine code
        cpu -- the CPU object whose memory will be written
        
        Return: number of bytes written to memory
        """
        
        # start form the given start adress
        current_address = start_address
        try:
            # Open the file and read line by line
            with open(filename, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    parts = self.parse_line(line)
                    if not parts:
                        continue
                    #the mnemonic is always the first instruction
                    mnemonic = parts[0]
                    #check if the mnemonic is valid
                    
                    if mnemonic not in self.instruction_set:
                        raise SyntaxError(f"Invalid instruction '{mnemonic}' at line {line_num}")
                    #get the format of the instruction
                
                    inst_format = self.instruction_set[mnemonic]
                    
                    # No operand instructions (e.g., HLT)
                    if inst_format['format'] == 'N':
                        #simply do and PC+= SIZER
                        opcode = self.get_opcode(mnemonic)
                        cpu.write_memory(current_address, opcode)
                        current_address += 1
                        
                    # Two-register instructions (e.g., MOV)
                    elif inst_format['format'] == 'RR':
                        # Check for valid number of operands
                        if len(parts) != 3:
                            raise SyntaxError(f"Invalid operands for {mnemonic} at line {line_num}")
                        #get the destination and source registers
                        dest, src = parts[1].strip(','), parts[2]
                        #get the opcode for the given mnemonic and operands
                        opcode = self.get_opcode(mnemonic, dest, src)
                        cpu.write_memory(current_address, opcode)
                        current_address += 1
                    # Register with immediate value (e.g., MVI)
                    elif inst_format['format'] == 'RI':
                        # Check for valid number of operands
                        if len(parts) != 3:
                            raise SyntaxError(f"Invalid operands for {mnemonic} at line {line_num}")
                        #get the destination register and immediate value
                        dest = parts[1].strip(',')
                        imm = int(parts[2].strip('H'), 16) if parts[2].endswith('H') else int(parts[2])
                        #write the opcode and immediate value to memory
                        opcode = self.get_opcode(mnemonic, dest)
                        cpu.write_memory(current_address, opcode)
                        cpu.write_memory(current_address + 1, imm)
                        current_address += 2
                    # Address-based instructions (e.g., LDA, STA)
                    elif inst_format['format'] == 'A':
                        # Check for valid number of operands
                        if len(parts) != 2:
                            raise SyntaxError(f"Invalid operands for {mnemonic} at line {line_num}")
                        
                        # Get the address value (16-bit)
                        addr = int(parts[1].strip('H'), 16) if parts[1].endswith('H') else int(parts[1])
                        # Write the opcode and address bytes to memory
                        opcode = self.get_opcode(mnemonic)
                        cpu.write_memory(current_address, opcode)
                        cpu.write_memory(current_address + 1, addr & 0xFF)
                        cpu.write_memory(current_address + 2, (addr >> 8) & 0xFF)
                        #PC+= size of the instruction type
                        current_address += 3
                    elif inst_format['format'] == 'RI1':
                        # Check for valid number of operands
                        if len(parts) != 2:
                            raise SyntaxError(f"Invalid operands for {mnemonic} at line {line_num}")
                        #get the immediate value
                        imm = int(parts[1].strip('H'), 16) if parts[1].endswith('H') else int(parts[1])
                        #write the opcode and immediate value to memory
                        opcode = self.get_opcode(mnemonic)
                        cpu.write_memory(current_address, opcode)
                        cpu.write_memory(current_address + 1, imm)
                        current_address += 2
                    elif inst_format['format'] == 'R1':
                        if len(parts) != 2:
                            raise SyntaxError(f"Invalid operands for {mnemonic} at line {line_num}")
                        
                        reg = parts[1]
                        opcode = self.get_opcode(mnemonic, src=reg)
                        cpu.write_memory(current_address, opcode)
                        current_address += 1

            return current_address - start_address  # Return number of bytes written
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            return 0
        except Exception as e:
            print(f"Error at line {line_num}: {str(e)}")
            return 0