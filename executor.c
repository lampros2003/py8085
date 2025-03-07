#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

// Function prototypes for memory access
typedef uint8_t (*ReadMemoryFunc)(uint16_t address);
typedef void (*WriteMemoryFunc)(uint16_t address, uint8_t value);

// Function prototypes for register access
typedef uint8_t (*ReadRegFunc)(uint8_t reg);
typedef void (*WriteRegFunc)(uint8_t reg, uint8_t value);
typedef uint8_t (*GetFlagsFunc)(void);
typedef void (*SetFlagsFunc)(uint8_t value);
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

static void update_flags(CPU8085Functions* cpu, uint8_t result) {
    uint8_t flags = 0;

    // Sign flag
    if (result & 0x80) flags |= FLAG_S;

    // Zero flag
    if (result == 0) flags |= FLAG_Z;

    // Parity flag calculation
    uint8_t parity = result;
    parity ^= parity >> 4;
    parity ^= parity >> 2;
    parity ^= parity >> 1;
    if (~parity & 1) flags |= FLAG_P;

    cpu->set_flags(flags);
}

__declspec(dllexport) int execute_instruction(CPU8085Functions* cpu) {
    uint16_t pc = cpu->get_pc();
    uint8_t opcode = cpu->read_memory(pc);
    printf("Executing opcode: %02X\n", opcode);
    printf("PC: %8X\n", pc);
    printf("A: %4X B: %4X C: %4X D: %4X E: %4X H: %4X L: %4X\n",
           cpu->read_reg(REG_A), cpu->read_reg(REG_B), cpu->read_reg(REG_C),
           cpu->read_reg(REG_D), cpu->read_reg(REG_E), cpu->read_reg(REG_H),
           cpu->read_reg(REG_L));
    printf("Carry= %d, Zero= %d, Sign= %d, Parity= %d, Aux Carry= %d\n",
           (cpu->get_flags() & FLAG_C) ? 1 : 0,
           (cpu->get_flags() & FLAG_Z) ? 1 : 0,
           (cpu->get_flags() & FLAG_S) ? 1 : 0,
           (cpu->get_flags() & FLAG_P) ? 1 : 0,
           (cpu->get_flags() & FLAG_AC) ? 1 : 0);
    printf("---------------------------------------\n");   
    

    // --- MVI Instruction (format: 00ddd110) ---
    if ((opcode & 0xC7) == 0x06) {
        uint8_t dest = (opcode >> 3) & 0x07;
        uint8_t imm = cpu->read_memory(pc + 1);
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

    uint8_t hi_nibble = opcode >> 4;
    switch(hi_nibble) {
        // --- NOP & Data Transfer Group ---
        case 0x0:
            if (opcode == 0x00) { // NOP
                cpu->set_pc(pc + 1);
                return 1;
            } else if ((opcode & 0x0F) == 0x1) { // LXI B, D, H, SP (00rp0001)
                uint8_t rp = (opcode >> 4) & 0x03;
                uint8_t low = cpu->read_memory(pc + 1);
                uint8_t high = cpu->read_memory(pc + 2);
                // Register pair decode logic would go here
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0x02 || opcode == 0x12) { // STAX B/D
                uint8_t rp = (opcode >> 4) & 0x01;
                // STAX implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0x0A || opcode == 0x1A) { // LDAX B/D
                uint8_t rp = (opcode >> 4) & 0x01;
                // LDAX implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if ((opcode & 0x0F) == 0x9) { // DAD B, D, H, SP (00rp1001)
                uint8_t rp = (opcode >> 4) & 0x03;
                // DAD implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if ((opcode & 0x0F) == 0x3) { // INX B, D, H, SP (00rp0011)
                uint8_t rp = (opcode >> 4) & 0x03;
                // INX implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if ((opcode & 0x0F) == 0xB) { // DCX B, D, H, SP (00rp1011)
                uint8_t rp = (opcode >> 4) & 0x03;
                // DCX implementation would go here
                cpu->set_pc(pc + 1);
                return 1;  
            }
            else if (opcode == 0x07) { // RLC
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0x0F) { // RRC
                cpu->set_pc(pc + 1);
                return 1;
            }
            break;
        case 0x1:
            if (opcode == 0x17) { // RAL
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0x1F) { // RAR
                cpu->set_pc(pc + 1);
                return 1;
            }
            break;
        // --- More Data Transfer & Special Group ---
        case 0x2:
            if (opcode == 0x22) { // SHLD addr
                uint8_t low = cpu->read_memory(pc + 1);
                uint8_t high = cpu->read_memory(pc + 2);
                // SHLD implementation would go here
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0x2A) { // LHLD addr
                uint8_t low = cpu->read_memory(pc + 1);
                uint8_t high = cpu->read_memory(pc + 2);
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
                uint8_t reg = (opcode >> 3) & 0x07;
                // INR implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if ((opcode & 0x07) == 0x5) { // DCR r (00rrr101)
                uint8_t reg = (opcode >> 3) & 0x07;
                // DCR implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            }
            else if (opcode == 0x2F) { // CMA
                cpu->set_pc(pc + 1);
                return 1;
            }
            break;

        // --- More Special Instructions ---
        case 0x3:
            if (opcode == 0x32) { // STA addr
                // ...existing code for STA...
            } else if (opcode == 0x3A) { // LDA addr
                // ...existing code for LDA...
            } else if (opcode == 0x30) { // SIM
                // SIM implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0x37) { // STC
                // STC implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0x3F) { // CMC
                // CMC implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            }
            break;

        // --- MOV Instructions ---
        case 0x4:
        case 0x5:
        case 0x6:
        case 0x7: {
            // Check for HLT (0x76) within 0x70 range
            if (opcode == 0x76) {
                // Halt execution
                return 0;
            }
            uint8_t dest = (opcode >> 3) & 0x07;
            uint8_t src  = opcode & 0x07;
            uint8_t value;
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
        }

        // --- Arithmetic Group ---
        case 0x8:
            if ((opcode & 0xF8) == 0x80) { // ADD r (10000rrr)
                // ...existing code for ADD...
            } else if ((opcode & 0xF8) == 0x88) { // ADC r (10001rrr)
                uint8_t src = opcode & 0x07;
                // ADC implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            }
            break;

        case 0x9:
            if ((opcode & 0xF8) == 0x90) { // SUB r (10010rrr)
                // ...existing code for SUB...
            } else if ((opcode & 0xF8) == 0x98) { // SBB r (10011rrr)
                uint8_t src = opcode & 0x07;
                // SBB implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            }
            break;

        // --- Logical Group ---
        case 0xA:
            if ((opcode & 0xF8) == 0xA0) { // ANA r (10100rrr)
                uint8_t src = opcode & 0x07;
                // ANA implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if ((opcode & 0xF8) == 0xA8) { // XRA r (10101rrr)
                uint8_t src = opcode & 0x07;
                // XRA implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            }
            break;
            
        case 0xB:
            if ((opcode & 0xF8) == 0xB0) { // ORA r (10110rrr)
                uint8_t src = opcode & 0x07;
                // ORA implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if ((opcode & 0xF8) == 0xB8) { // CMP r (10111rrr)
                uint8_t src = opcode & 0x07;
                // CMP implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            }
            break;

        // --- Branch, Stack, and I/O Group ---
        case 0xC:
            if (opcode == 0xC3) { // JMP addr
                uint8_t low = cpu->read_memory(pc + 1);
                uint8_t high = cpu->read_memory(pc + 2);
                uint16_t addr = ((uint16_t)high << 8) | low;
                cpu->set_pc(addr);
                return 1;
            } else if (opcode == 0xC2) { // JNZ addr
                uint8_t low = cpu->read_memory(pc + 1);
                uint8_t high = cpu->read_memory(pc + 2);
                uint16_t addr = ((uint16_t)high << 8) | low;
                // JNZ implementation would go here
                cpu->set_pc(pc + 3); // If condition not met
                return 1;
            } else if (opcode == 0xCA) { // JZ addr
                uint8_t low = cpu->read_memory(pc + 1);
                uint8_t high = cpu->read_memory(pc + 2);
                uint16_t addr = ((uint16_t)high << 8) | low;
                // JZ implementation would go here
                cpu->set_pc(pc + 3); // If condition not met
                return 1;
            } else if (opcode == 0xC6) { // ADI data
                uint8_t imm = cpu->read_memory(pc + 1);
                uint8_t acc = cpu->read_reg(REG_A);
                uint8_t result = acc + imm;
                update_flags(cpu, result);
                cpu->write_reg(REG_A, result);
                cpu->set_pc(pc + 2);
                return 1;

            } else if (opcode == 0xCD) { // CALL addr
                uint8_t low = cpu->read_memory(pc + 1);
                uint8_t high = cpu->read_memory(pc + 2);
                // CALL implementation would go here
                cpu->set_pc(pc + 3);
                return 1;
            } else if ((opcode & 0xCF) == 0xC1) { // POP rp (11rp0001)
                uint8_t rp = (opcode >> 4) & 0x03;
                // POP implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if ((opcode & 0xCF) == 0xC5) { // PUSH rp (11rp0101)
                uint8_t rp = (opcode >> 4) & 0x03;
                // PUSH implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0xC9) { // RET
                // RET implementation would go here
                return 1;
            }
            else if (opcode == 0xCE) { // ACI
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
            }
            break;

        case 0xD:
            if (opcode == 0xD3) { // OUT port
                uint8_t port = cpu->read_memory(pc + 1);
                // OUT implementation would go here
                cpu->set_pc(pc + 2);
                return 1;
            } else if (opcode == 0xDB) { // IN port
                uint8_t port = cpu->read_memory(pc + 1);
                // IN implementation would go here
                cpu->set_pc(pc + 2);
                return 1;
            } else if (opcode == 0xD2) { // JNC addr
                uint8_t low = cpu->read_memory(pc + 1);
                uint8_t high = cpu->read_memory(pc + 2);
                // JNC implementation would go here
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0xDA) { // JC addr
                uint8_t low = cpu->read_memory(pc + 1);
                uint8_t high = cpu->read_memory(pc + 2);
                // JC implementation would go here
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0xD6) { // SUI data
                uint8_t imm = cpu->read_memory(pc + 1);
                // SUI implementation would go here
                cpu->set_pc(pc + 2);
                return 1; 
            }
            else if (opcode == 0xDE) { // SBI
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
            }
            break;

        case 0xE:
            if (opcode == 0xEB) { // XCHG
                // XCHG implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0xE3) { // XTHL
                // XTHL implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            } else if (opcode == 0xE6) { // ANI data
                uint8_t imm = cpu->read_memory(pc + 1);
                // ANI implementation would go here
                cpu->set_pc(pc + 2);
                return 1;
            } else if (opcode == 0xE9) { // PCHL
                // PCHL implementation would go here
                return 1;
            } else if (opcode == 0xE2) { // JPO addr
                uint8_t low = cpu->read_memory(pc + 1);
                uint8_t high = cpu->read_memory(pc + 2);
                // JPO implementation would go here
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0xEA) { // JPE addr
                uint8_t low = cpu->read_memory(pc + 1);
                uint8_t high = cpu->read_memory(pc + 2);
                // JPE implementation would go here
                cpu->set_pc(pc + 3);
                return 1;
            }
            else if (opcode == 0xEE) { // XRI
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
            }
            break;

        case 0xF:
            if (opcode == 0xF6) { // ORI data
                uint8_t imm = cpu->read_memory(pc + 1);
                // ORI implementation would go here
                cpu->set_pc(pc + 2);
                return 1;
            } else if (opcode == 0xFE) { // CPI data
                uint8_t imm = cpu->read_memory(pc + 1);
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
                uint8_t low = cpu->read_memory(pc + 1);
                uint8_t high = cpu->read_memory(pc + 2);
                // JP implementation would go here
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0xFA) { // JM addr
                uint8_t low = cpu->read_memory(pc + 1);
                uint8_t high = cpu->read_memory(pc + 2);
                // JM implementation would go here
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0xF9) { // SPHL
                // SPHL implementation would go here
                cpu->set_pc(pc + 1);
                return 1;
            }
            else if (opcode == 0xF4) { // CP
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