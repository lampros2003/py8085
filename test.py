import py8085 as py85
import assembler 

if __name__ == "__main__":
    memory = py85.Memory()
    registers = py85.Registers()
    
    test_cpu = py85.CPU8085(memory=memory, registers=registers)
    
    asm = assembler.assembler()
    assembled_bytes = asm.assemble('test.asm', 0x0000, cpu=test_cpu)
    print(f"Total {assembled_bytes} bytes assembled.")
    
    test_cpu.execute()  
    
    
    
    
    

