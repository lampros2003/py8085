import py8085 as py85
import assembler 
if __name__ == "__main__":
    # Run assembler (assemble code into global memory)
    asm = assembler.assembler()
    test_cpu = py85.CPU8085()
    assembled_bytes = asm.assemble('test.asm', 0x0000, cpu=test_cpu)
    print(f"Total {assembled_bytes} bytes assembled.")

    # Create a CPU instance and execute instructions from memory
    
    test_cpu.execute()  # This calls executor_dll.execute_instruction repeatedly
    
    