// registers.c

#include <stdint.h>




typedef struct {
    uint8_t A, B, C, D, E, H, L;
    uint16_t PC, SP;
    uint8_t flags; // Pack flags into a byte (e.g., bit 0 = Carry, bit 1 = Zero, etc.)
} Registers;// 8085 has 8-bit registers and 16-bit PC and SP all are in the same structure for easy access  

static Registers reg;
uint8_t read_reg(uint8_t reg_num) {
    switch (reg_num) {
    case 0: return reg.A;
    case 1: return reg.B;
    case 2: return reg.C;
    case 3: return reg.D;
    case 4: return reg.E;
    case 5: return reg.H;
    case 6: return reg.L;    
    }
    return 0;
}
void write_reg(uint8_t reg_num, uint8_t value) {
    switch (reg_num) {
    case 0: reg.A = value; break;
    case 1: reg.B = value; break;
    case 2: reg.C = value; break;
    case 3: reg.D = value; break;
    case 4: reg.E = value; break;
    case 5: reg.H = value; break;
    case 6: reg.L = value; break;
    }
}

uint8_t get_flags() { return reg.flags; }
void set_flags(uint8_t value) { reg.flags = value; }

uint16_t get_PC() { return reg.PC; }
void set_PC(uint16_t value) { reg.PC = value; }


uint16_t get_SP() { return reg.SP; }
void set_SP(uint16_t value) { reg.SP = value; }