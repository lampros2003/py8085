#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

// Function prototypes for memory access
typedef int8_t (*ReadMemoryFunc)(uint16_t address);
typedef void (*WriteMemoryFunc)(uint16_t address, int8_t value);

// Function prototypes for register access
typedef int8_t (*ReadRegFunc)(int8_t reg);
typedef void (*WriteRegFunc)(int8_t reg, int8_t value);
typedef int8_t (*GetFlagsFunc)(void);
typedef void (*SetFlagsFunc)(int8_t value);
typedef uint16_t (*GetPCFunc)(void);
typedef void (*SetPCFunc)(uint16_t value);
typedef uint16_t (*GetSPFunc)(void);
typedef void (*SetSPFunc)(uint16_t value);

// Structure to hold all function pointers
typedef struct {
    ReadMemoryFunc read_memory;
    WriteMemoryFunc write_memory;
    ReadRegFunc read_reg;
    WriteRegFunc write_reg;
    GetFlagsFunc get_flags;
    SetFlagsFunc set_flags;
    GetPCFunc get_pc;
    SetPCFunc set_pc;
    GetSPFunc get_sp;
    SetSPFunc set_sp;
} CPU8085Functions;

// Flag bit positions
#define FLAG_S  0x80
#define FLAG_Z  0x40
#define FLAG_AC 0x10
#define FLAG_P  0x04
#define FLAG_C  0x01

// Register indices
#define REG_B 0
#define REG_C 1
#define REG_D 2
#define REG_E 3
#define REG_H 4
#define REG_L 5
#define REG_M 6
#define REG_A 7

static void update_flags(CPU8085Functions* cpu, int8_t result) {
    int8_t flags = 0;

    // Sign flag
    if (result & 0x80) flags |= FLAG_S;

    // Zero flag
    if (result == 0) flags |= FLAG_Z;

    // Parity flag calculation
    int8_t parity = result;
    parity ^= parity >> 4;
    parity ^= parity >> 2;
    parity ^= parity >> 1;
    if (~parity & 1) flags |= FLAG_P;

    cpu->set_flags(flags);
}
int accum ;
int temp;

__declspec(dllexport) int execute_instruction(CPU8085Functions* cpu) {
    uint16_t pc = cpu->get_pc();
    int8_t opcode = cpu->read_memory(pc);
    printf("Executing opcode: %02X\n", opcode);
    printf("PC: %8X\n", pc);
    printf("A: %4X B: %4X C: %4X D: %4X E: %4X H: %4X L: %4X\n",
           cpu->read_reg(REG_A), cpu->read_reg(REG_B), cpu->read_reg(REG_C),
           cpu->read_reg(REG_D), cpu->read_reg(REG_E), cpu->read_reg(REG_H),
           cpu->read_reg(REG_L));
    printf("SP: %8X\n", cpu->get_sp());

    printf("Carry= %d, Zero= %d, Sign= %d, Parity= %d, Aux Carry= %d\n",
           (cpu->get_flags() & FLAG_C) ? 1 : 0,
           (cpu->get_flags() & FLAG_Z) ? 1 : 0,
           (cpu->get_flags() & FLAG_S) ? 1 : 0,
           (cpu->get_flags() & FLAG_P) ? 1 : 0,
           (cpu->get_flags() & FLAG_AC) ? 1 : 0);
    printf("---------------------------------------\n");   
    
    // --- MVI Instruction (format: 00ddd110) ---
    if ((opcode & 0xC7) == 0x06) {
        int8_t dest = (opcode >> 3) & 0x07;
        int8_t imm = cpu->read_memory(pc + 1);
        if (dest == REG_M) {
            // For MVI M, the effective address is in the register pair H and L.
            uint16_t addr = ((uint16_t)cpu->read_reg(REG_H) << 8) | cpu->read_reg(REG_L);
            cpu->write_memory(addr, imm);
        } else {
            cpu->write_reg(dest, imm);
        }
        cpu->set_pc(pc + 2);
        return 1;
    }

    // Switch based on the first two bits of the opcode
    int8_t hi_bits = opcode >> 6;
    switch(hi_bits) {
        // 00: Miscellaneous and register operations
        case 0x0:
            if (opcode == 0x00) { // NOP
                cpu->set_pc(pc + 1);
                return 1;
            } else if ((opcode & 0x0F) == 0x1) { // LXI B, D, H, SP (00rp0001)
                int8_t rp = (opcode >> 4) & 0x03;
                int8_t low = cpu->read_memory(pc + 1);
                int8_t high = cpu->read_memory(pc + 2);
                switch (rp) {
                    case 0: // BC
                        cpu->write_reg(REG_C, low);
                        cpu->write_reg(REG_B, high);
                        break;
                    case 1: // DE
                        cpu->write_reg(REG_E, low);
                        cpu->write_reg(REG_D, high);
                        break;
                    case 2: // HL
                        cpu->write_reg(REG_L, low);
                        cpu->write_reg(REG_H, high);
                        break;
                    case 3: // SP
                        cpu->set_sp(((uint16_t)high << 8) | low);
                        break;
                }
                
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0x02 || opcode == 0x12) { // STAX B/D
                int8_t rp = (opcode >> 4) & 0x01;
                //fetch the value from the accumulator and store it in the memory location pointed by the register pair
                int8_t value = cpu->read_reg(REG_A);
                uint16_t addr;
                switch (rp) {
                    case 0: // BC
                        addr= ((uint16_t)cpu->read_reg(REG_B) << 8) | cpu->read_reg(REG_C);
                        cpu->write_memory(addr, value);
                       break;
                    case 1: // DE
                        addr = ((uint16_t)cpu->read_reg(REG_D) << 8) | cpu->read_reg(REG_E);
                        cpu->write_memory(addr, value);
                        break;
                    case 2: // HL
                        addr = ((uint16_t)cpu->read_reg(REG_H) << 8) | cpu->read_reg(REG_L);
                        cpu->write_memory(addr, value);
                        break;
                    case 3: // SP
                        addr = cpu->get_sp();
                        cpu->write_memory(addr, value);
                        break;
                       
                }
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0x0A || opcode == 0x1A) { // LDAX B/D
                int8_t rp = (opcode >> 4) & 0x01;
                // LDAX implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if ((opcode & 0x0F) == 0x9) { // DAD B, D, H, SP (00rp1001)
                int8_t rp = (opcode >> 4) & 0x03;
                // DAD implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if ((opcode & 0x0F) == 0x3) { // INX B, D, H, SP (00rp0011)
                int8_t rp = (opcode >> 4) & 0x03;
                // INX implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if ((opcode & 0x0F) == 0xB) { // DCX B, D, H, SP (00rp1011) implemented
                int8_t rp = (opcode >> 4) & 0x03;
                switch (rp) {
                    case 0: // BC
                        temp = cpu->read_reg(REG_C);
                        temp--;
                        if(temp < 0)
                        {
                            cpu->write_reg(REG_C, 0xFF);
                            cpu->write_reg(REG_B, cpu->read_reg(REG_B)-1);
                        }
                        else
                        {
                            cpu->write_reg(REG_C, temp);
                        }
                        break;
                    case 1: // DE
                        temp = cpu->read_reg(REG_E);
                        temp--;
                        if(temp < 0)
                        {
                            cpu->write_reg(REG_E, 0xFF);
                            cpu->write_reg(REG_D, cpu->read_reg(REG_D)-1);
                        }
                        else
                        {
                            cpu->write_reg(REG_E, temp);
                        }
                        break;
                    case 2: // HL
                        temp = cpu->read_reg(REG_L);
                        temp--;
                        if(temp < 0)
                        {
                            cpu->write_reg(REG_L, 0xFF);
                            cpu->write_reg(REG_H, cpu->read_reg(REG_H)-1);
                        }
                        else
                        {
                            cpu->write_reg(REG_L, temp);
                        }
                        break;
                    case 3: // SP
                        temp = cpu->get_sp();
                        temp--;
                        cpu->set_sp(temp);
                        break;
                }
                
                cpu->set_pc(pc + 1);
                return 1;  
            } else if (opcode == 0x07) { // RLC
                

                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0x0F) { // RRC

                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0x17) { // RAL
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0x1F) { // RAR
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0x22) { // SHLD addr
                int8_t low = cpu->read_memory(pc + 1);
                int8_t high = cpu->read_memory(pc + 2);
                // SHLD implementation would go here
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0x2A) { // LHLD addr
                int8_t low = cpu->read_memory(pc + 1);
                int8_t high = cpu->read_memory(pc + 2);
                // LHLD implementation would go here
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0x20) { // RIM
                // RIM implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0x27) { // DAA
                // DAA implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if ((opcode & 0x07) == 0x4) { // INR r (00rrr100)
                int8_t reg = (opcode >> 3) & 0x07;
                // INR implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if ((opcode & 0x07) == 0x5) { // DCR r (00rrr101)
                int8_t reg = (opcode >> 3) & 0x07;
                // DCR implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0x2F) { // CMA
                cpu->set_pc(pc + 1);
                return 1;
            }
            break;

        // 01: MOV and HLT
        case 0x1:
            // Check for HLT (0x76) within 0x70 range
            if (opcode == 0x76) {
                // Halt execution
                return 0;
            }
            int8_t dest = (opcode >> 3) & 0x07;
            int8_t src  = opcode & 0x07;
            int8_t value;
            // If source is memory (M), read from address in H and L.
            if (src == REG_M) {
                uint16_t addr = ((uint16_t)cpu->read_reg(REG_H) << 8) | cpu->read_reg(REG_L);
                value = cpu->read_memory(addr);
            } else {
                value = cpu->read_reg(src);
            }
            // If destination is memory (M), write the value to memory at address from (H,L).
            if (dest == REG_M) {
                uint16_t addr = ((uint16_t)cpu->read_reg(REG_H) << 8) | cpu->read_reg(REG_L);
                cpu->write_memory(addr, value);
            } else {
                cpu->write_reg(dest, value);
            }
            cpu->set_pc(pc + 1);
            return 1;

        // 10: Arithmetic and logical operations
        case 0x2:
            if ((opcode & 0xF8) == 0x80) { // ADD r (10000rrr)
                int8_t src = opcode & 0x07;
                int8_t result = cpu->read_reg(REG_A) + cpu->read_reg(src);
                update_flags(cpu, result);
                cpu->write_reg(REG_A, result);
                cpu->set_pc(pc + 1);
                return 1;
            } else if ((opcode & 0xF8) == 0x88) { // ADC r (10001rrr)
                int8_t src = opcode & 0x07;
                // ADC implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if ((opcode & 0xF8) == 0x90) { // SUB r (10010rrr)
                int8_t src = opcode & 0x07;
                int8_t result = cpu->read_reg(REG_A) - cpu->read_reg(src);
                update_flags(cpu, result);
                cpu->write_reg(REG_A, result);
                cpu->set_pc(pc + 1);
                return 1;
            } else if ((opcode & 0xF8) == 0x98) { // SBB r (10011rrr)
                int8_t src = opcode & 0x07;
                // SBB implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if ((opcode & 0xF8) == 0xA0) { // ANA r (10100rrr)
                int8_t src = opcode & 0x07;
                // ANA implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if ((opcode & 0xF8) == 0xA8) { // XRA r (10101rrr)
                int8_t src = opcode & 0x07;
                // XRA implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if ((opcode & 0xF8) == 0xB0) { // ORA r (10110rrr)
                int8_t src = opcode & 0x07;
                // ORA implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if ((opcode & 0xF8) == 0xB8) { // CMP r (10111rrr)
                int8_t src = opcode & 0x07;
                // CMP implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            }
            break;

        // 11: Branch, stack, and I/O operations
        case 0x3:
            
            if (opcode == 0xC3) { // JMP addr
                int8_t low = cpu->read_memory(pc + 1);
                int8_t high = cpu->read_memory(pc + 2);
                uint16_t addr = ((uint16_t)high << 8) | low;
                cpu->set_pc(addr);
                return 1;
            } else if (opcode == 0xC2) { // JNZ addr
                int8_t low = cpu->read_memory(pc + 1);
                int8_t high = cpu->read_memory(pc + 2);
                uint16_t addr = ((uint16_t)high << 8) | low;
                if (!(cpu->get_flags() & FLAG_Z)) {
                    cpu->set_pc(addr);
                } else {
                    cpu->set_pc(pc + 3); // If condition not met
                }
                return 1;
            } else if (opcode == 0xCA) { // JZ addr
                int8_t low = cpu->read_memory(pc + 1);
                int8_t high = cpu->read_memory(pc + 2);
                uint16_t addr = ((uint16_t)high << 8) | low;
                if (cpu->get_flags() & FLAG_Z) {
                    cpu->set_pc(addr);
                } else {
                    cpu->set_pc(pc + 3);
                }
                return 1;
            } else if (opcode == 0xC6) { // ADI data
                int8_t result = cpu->read_reg(REG_A) + cpu->read_memory(pc + 1);
                update_flags(cpu, result);
                cpu->write_reg(REG_A, result);
                cpu->set_pc(pc + 2);
                return 1;
            } else if (opcode == 0xCD) { // CALL addr
                int8_t low = cpu->read_memory(pc + 1);
                int8_t high = cpu->read_memory(pc + 2);
                // CALL implementation would go here
                cpu->set_pc(pc + 3);
                return 1;
            } else if ((opcode & 0xCF) == 0xC1) { // POP rp (11rp0001)
                int8_t rp = (opcode >> 4) & 0x03;
                uint16_t sp = cpu->get_sp();
                int8_t low = cpu->read_memory(sp);
                int8_t high = cpu->read_memory(sp + 1);
                printf("POP\n");
                printf("SP: %8X\n", sp);
                printf("sp-1: %8X\n", sp - 1);
                printf("sp-2: %8X\n", sp - 2);
                printf("rp: %d\n", rp);
                switch (rp) {
                    case 0: // BC
                        cpu->write_reg(REG_C, low);
                        cpu->write_reg(REG_B, high);
                        break;
                    case 1: // DE
                        cpu->write_reg(REG_E, low);
                        cpu->write_reg(REG_D, high);
                        break;
                    case 2: // HL
                        cpu->write_reg(REG_L, low);
                        cpu->write_reg(REG_H, high);
                        break;
                    case 3: // AF || system state
                        cpu->write_reg(REG_A, high);
                        cpu->set_flags(low);
                        break;
                }
                cpu->set_sp(sp + 2);
                cpu->set_pc(pc + 1);
                return 1;
            } else if ((opcode & 0xCF) == 0xC5) { // PUSH rp (11rp0101)
                // Extract register pair bits (bits 5-4 of opcode)
                int8_t rp = (opcode & 0x30) >> 4; // More explicit extraction of bits 5-4
                uint16_t sp = cpu->get_sp();
                printf("Push\n");
                printf("SP: %8X\n", sp);
                printf("sp-1: %8X\n", sp - 1);
                printf("sp-2: %8X\n", sp - 2);
                printf("rp: %d (opcode: 0x%02X)\n", rp, opcode);
                switch (rp) {
                    case 0: // BC
                        cpu->write_memory(sp - 1, cpu->read_reg(REG_B));
                        cpu->write_memory(sp - 2, cpu->read_reg(REG_C));
                        break;
                    case 1: // DE
                        cpu->write_memory(sp - 1, cpu->read_reg(REG_D));
                        cpu->write_memory(sp - 2, cpu->read_reg(REG_E));
                        break;
                    case 2: // HL
                        cpu->write_memory(sp - 1, cpu->read_reg(REG_H));
                        cpu->write_memory(sp - 2, cpu->read_reg(REG_L));
                        break;
                    case 3: // AF (PSW)
                        cpu->write_memory(sp - 1, cpu->read_reg(REG_A));
                        cpu->write_memory(sp - 2, cpu->get_flags());
                        break;
                }
                cpu->set_sp(sp - 2);
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0xC9) { // RET
                // RET implementation would go here
                return 1;
            } else if (opcode == 0xCE) { // ACI
                cpu->set_pc(pc + 2);
                return 1;
            } else if (opcode == 0xCC) { // CZ
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0xC4) { // CNZ
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0xC8) { // RZ
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0xC0) { // RNZ
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0xC7) { // RST
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0xD3) { // OUT port
                int8_t port = cpu->read_memory(pc + 1);
                // OUT implementation would go here
                cpu->set_pc(pc + 2);
                return 1;
            } else if (opcode == 0xDB) { // IN port
                int8_t port = cpu->read_memory(pc + 1);
                // IN implementation would go here
                cpu->set_pc(pc + 2);
                return 1;
            } else if (opcode == 0xD2) { // JNC addr
                int8_t low = cpu->read_memory(pc + 1);
                int8_t high = cpu->read_memory(pc + 2);
                // JNC implementation would go here
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0xDA) { // JC addr
                int8_t low = cpu->read_memory(pc + 1);
                int8_t high = cpu->read_memory(pc + 2);
                // JC implementation would go here
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0xD6) { // SUI data
                int8_t imm = cpu->read_memory(pc + 1);
                // SUI implementation would go here
                cpu->set_pc(pc + 2);
                return 1;
            } else if (opcode == 0xDE) { // SBI
                cpu->set_pc(pc + 2);
                return 1;
            } else if (opcode == 0xDC) { // CC
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0xD4) { // CNC
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0xD8) { // RC
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0xD0) { // RNC
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0xEB) { // XCHG
                // XCHG implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0xE3) { // XTHL
                // XTHL implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0xE6) { // ANI data
                int8_t imm = cpu->read_memory(pc + 1);
                // ANI implementation would go here
                cpu->set_pc(pc + 2);
                return 1;
            } else if (opcode == 0xE9) { // PCHL
                // PCHL implementation would go here
                return 1;
            } else if (opcode == 0xE2) { // JPO addr
                int8_t low = cpu->read_memory(pc + 1);
                int8_t high = cpu->read_memory(pc + 2);
                // JPO implementation would go here
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0xEA) { // JPE addr
                int8_t low = cpu->read_memory(pc + 1);
                int8_t high = cpu->read_memory(pc + 2);
                // JPE implementation would go here
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0xEE) { // XRI
                cpu->set_pc(pc + 2);
                return 1;
            } else if (opcode == 0xEC) { // CPE
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0xE4) { // CPO
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0xE8) { // RPE
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0xE0) { // RPO
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0xF6) { // ORI data
                int8_t imm = cpu->read_memory(pc + 1);
                // ORI implementation would go here
                cpu->set_pc(pc + 2);
                return 1;
            } else if (opcode == 0xFE) { // CPI data
                int8_t imm = cpu->read_memory(pc + 1);
                // CPI implementation would go here
                cpu->set_pc(pc + 2);
                return 1;
            } else if (opcode == 0xF3) { // DI
                // DI implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0xFB) { // EI
                // EI implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0xF2) { // JP addr
                if (cpu->get_flags() & FLAG_S) {
                    int8_t low = cpu->read_memory(pc + 1);
                    int8_t high = cpu->read_memory(pc + 2);
                    uint16_t addr = ((uint16_t)high << 8) | low;
                    cpu->set_pc(addr);
                } else {
                    cpu->set_pc(pc + 3);
                }
                break;
            } else if (opcode == 0xFA) { // JM addr
                if (cpu->get_flags() & !FLAG_S) {
                    int8_t low = cpu->read_memory(pc + 1);
                    int8_t high = cpu->read_memory(pc + 2);
                    uint16_t addr = ((uint16_t)high << 8) | low;
                    cpu->set_pc(addr);
                } else {
                    cpu->set_pc(pc + 3);
                }
                break;
            } else if (opcode == 0xF9) { // SPHL
                cpu->set_sp(((uint16_t)cpu->read_reg(REG_H) << 8) | cpu->read_reg(REG_L));
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0xF4) { // CP
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0xFC) { // CM
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0xF0) { // RP
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0xF8) { // RM
                cpu->set_pc(pc + 1);
                return 1;
            }
            break;

        default:
            break;
    }
    
    // If we reach here, the opcode is unknown
    return -1;
}