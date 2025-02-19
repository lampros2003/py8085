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
    printf("PC: %04X\n", pc);
    printf("A: %02X B: %02X C: %02X D: %02X E: %02X H: %02X L: %02X\n",
           cpu->read_reg(REG_A), cpu->read_reg(REG_B), cpu->read_reg(REG_C),
           cpu->read_reg(REG_D), cpu->read_reg(REG_E), cpu->read_reg(REG_H),
           cpu->read_reg(REG_L));

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
        // --- NOP (0x00) ---
        case 0x0:
            if (opcode == 0x00) { // NOP
                cpu->set_pc(pc + 1);
                return 1;
            }
            break;

        // --- MOV Instructions (opcodes 0x40 to 0x7F) ---
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

        // --- LDA and STA (opcodes 0x3A and 0x32) ---
        case 0x3: {
            if (opcode == 0x3A) { // LDA addr
                // Assembled as: opcode, low byte, high byte
                uint8_t low = cpu->read_memory(pc + 1);
                uint8_t high = cpu->read_memory(pc + 2);
                uint16_t addr = ((uint16_t)high << 8) | low;
                uint8_t data = cpu->read_memory(addr);
                cpu->write_reg(REG_A, data);
                cpu->set_pc(pc + 3);
                return 1;
            } else if (opcode == 0x32) { // STA addr
                uint8_t low = cpu->read_memory(pc + 1);
                uint8_t high = cpu->read_memory(pc + 2);
                uint16_t addr = ((uint16_t)high << 8) | low;
                uint8_t data = cpu->read_reg(REG_A);
                cpu->write_memory(addr, data);
                cpu->set_pc(pc + 3);
                return 1;
            }
            break;
        }

        // --- ADD Instruction (opcodes 0x80 to 0x87) ---
        case 0x8: {
            uint8_t src = opcode & 0x07; // Register operand code
            uint8_t A = cpu->read_reg(REG_A);
            uint8_t operand;
            if (src == REG_M) {
                uint16_t addr = ((uint16_t)cpu->read_reg(REG_H) << 8) | cpu->read_reg(REG_L);
                operand = cpu->read_memory(addr);
            } else {
                operand = cpu->read_reg(src);
            }
            uint8_t result = A + operand;
            cpu->write_reg(REG_A, result);
            printf("A: %02X, Operand: %02X\n", A, operand);
            printf("Result: %02X\n", result);
            update_flags(cpu, result);
            
            cpu->set_pc(pc + 1);
            printf("PC: %04X\n", cpu->get_pc());   
            return 1;
        }

        // --- SUB Instruction (opcodes 0x90 to 0x97) ---
        case 0x9: {
            uint8_t src = opcode & 0x07;
            uint8_t A = cpu->read_reg(REG_A);
            uint8_t operand;
            if (src == REG_M) {
                uint16_t addr = ((uint16_t)cpu->read_reg(REG_H) << 8) | cpu->read_reg(REG_L);
                operand = cpu->read_memory(addr);
            } else {
                operand = cpu->read_reg(src);
            }
            uint8_t result = A - operand;
            cpu->write_reg(REG_A, result);
            update_flags(cpu, result);
            cpu->set_pc(pc + 1);
            return 1;
        }

        // --- ADI (Add Immediate) Instruction (opcode 0xC6) ---
        case 0xC: {
            if (opcode == 0xC6) {
                uint8_t imm = cpu->read_memory(pc + 1);
                uint8_t A = cpu->read_reg(REG_A);
                uint8_t result = A + imm;
                cpu->write_reg(REG_A, result);
                update_flags(cpu, result);
                cpu->set_pc(pc + 2);
                return 1;
            }
            break;
        }

        // --- SUI (Subtract Immediate) Instruction (opcode 0xD6) ---
        case 0xD: {
            if (opcode == 0xD6) {
                uint8_t imm = cpu->read_memory(pc + 1);
                uint8_t A = cpu->read_reg(REG_A);
                uint8_t result = A - imm;
                cpu->write_reg(REG_A, result);
                update_flags(cpu, result);
                cpu->set_pc(pc + 2);
                return 1;
            }
            break;
        }

        default:
            break;
    }
    
    // If we reach here, the opcode is unknown
    return -1;
}