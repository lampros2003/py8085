#include <stdint.h>

// Register definitions
static uint8_t registers[8] = {0};  // A,B,C,D,E,H,L,M
static uint8_t flags = 0;
static uint16_t PC = 0;
static uint16_t SP = 0;

__declspec(dllexport) uint8_t read_reg(uint8_t reg) {
    if(reg < 8) return registers[reg];
    return 0;
}

__declspec(dllexport) void write_reg(uint8_t reg, uint8_t value) {
    if(reg < 8) registers[reg] = value;
}

__declspec(dllexport) uint8_t get_flags(void) {
    return flags;
}

__declspec(dllexport) void set_flags(uint8_t value) {
    flags = value;
}

__declspec(dllexport) uint16_t get_PC(void) {
    return PC;
}

__declspec(dllexport) void set_PC(uint16_t value) {
    PC = value;
}

__declspec(dllexport) uint16_t get_SP(void) {
    return SP;
}

__declspec(dllexport) void set_SP(uint16_t value) {
    SP = value;
}