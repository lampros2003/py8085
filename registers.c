#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int8_t regs[8]; // A,B,C,D,E,H,L,M
    int8_t flags;
    uint16_t PC;
    uint16_t SP;
} Registers;


__declspec(dllexport) Registers* create_registers() {
    Registers* r = (Registers*)malloc(sizeof(Registers));
    memset(r, 0, sizeof(Registers));
    return r;
}

__declspec(dllexport) void destroy_registers(Registers* r) {
    free(r);
}

__declspec(dllexport) int8_t read_reg(Registers* r, int8_t reg) {
    if (reg < 8) return r->regs[reg];
    return 0;
}

__declspec(dllexport) void write_reg(Registers* r, int8_t reg, int8_t value) {
    if (reg < 8) r->regs[reg] = value;
}

__declspec(dllexport) int8_t get_flags(Registers* r) {
    return r->flags;
}

__declspec(dllexport) void set_flags(Registers* r, int8_t value) {
    r->flags = value;
}

__declspec(dllexport) uint16_t get_PC(Registers* r) {
    return r->PC;
}

__declspec(dllexport) void set_PC(Registers* r, uint16_t value) {
    r->PC = value;
}

__declspec(dllexport) uint16_t get_SP(Registers* r) {
    return r->SP;
}

__declspec(dllexport) void set_SP(Registers* r, uint16_t value) {
    r->SP = value;
}