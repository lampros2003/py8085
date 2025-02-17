#include <stdint.h>
#include <stdbool.h>

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
#define REG_A 0
#define REG_B 1
#define REG_C 2
#define REG_D 3
#define REG_E 4
#define REG_H 5
#define REG_L 6
#define REG_M 7

static void update_flags(CPU8085Functions* cpu, uint8_t result) {
    uint8_t flags = 0;
    
    // Sign flag
    if (result & 0x80) flags |= FLAG_S;
    
    // Zero flag
    if (result == 0) flags |= FLAG_Z;
    
    // Parity flag
    uint8_t parity = result;
    parity ^= parity >> 4;
    parity ^= parity >> 2;
    parity ^= parity >> 1;
    if (~parity & 1) flags |= FLAG_P;
    
    cpu->set_flags(flags);
}

__declspec(dllexport) bool execute_instruction(CPU8085Functions* cpu) {
    uint16_t pc = cpu->get_pc();
    uint8_t opcode = cpu->read_memory(pc);

    // Check for MVI instruction (format: 00ddd110)
    // Mask with 0xC7 (1100 0111) so that any opcode that, when masked, equals 0x06 is treated as MVI.
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
        return true;
    }
    
    uint8_t hi_nibble = opcode >> 4;
    
    switch(hi_nibble) {
        case 0x0: // NOP and other 0x0x instructions
            if (opcode == 0x00) { // NOP
                cpu->set_pc(pc + 1);
                return true;
            }
            break;
            
        case 0x4: // MOV instructions (01dddsss)
        case 0x5:
        case 0x6:
        case 0x7: 
        if (opcode == 0x76) { // HLT
            return false;
        }
        
        else
        {
            uint8_t dest = (opcode >> 3) & 0x07;
            uint8_t src = opcode & 0x07;
            uint8_t value;
            
            // If source is M, then use memory pointed by (H,L)
            if (src == REG_M) {
                uint16_t addr = ((uint16_t)cpu->read_reg(REG_H) << 8) | cpu->read_reg(REG_L);
                value = cpu->read_memory(addr);
            } else {
                value = cpu->read_reg(src);
            }
            
            // If destination is M, write the value to memory pointed by (H,L)
            if (dest == REG_M) {
                uint16_t addr = ((uint16_t)cpu->read_reg(REG_H) << 8) | cpu->read_reg(REG_L);
                cpu->write_memory(addr, value);
            } else {
                cpu->write_reg(dest, value);
            }
            
            cpu->set_pc(pc + 1);
            return true;
        }
        
        case 0x3: {
            if (opcode == 0x3A) { // LDA addr
                // In the assembler, address is stored as: opcode, low byte, then high byte
                uint8_t low = cpu->read_memory(pc + 1);
                uint8_t high = cpu->read_memory(pc + 2);
                uint16_t addr = ((uint16_t)high << 8) | low;
                uint8_t data = cpu->read_memory(addr);
                cpu->write_reg(REG_A, data);
                cpu->set_pc(pc + 3);
                return true;
            } else if (opcode == 0x32) { // STA addr
                uint8_t low = cpu->read_memory(pc + 1);
                uint8_t high = cpu->read_memory(pc + 2);
                uint16_t addr = ((uint16_t)high << 8) | low;
                uint8_t data = cpu->read_reg(REG_A);
                cpu->write_memory(addr, data);
                cpu->set_pc(pc + 3);
                return true;
            }
            break;
        }
        
        
    }
    
    // Unknown opcode
    return false;
}