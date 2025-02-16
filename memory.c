#include <stdint.h>

#define MEMORY_SIZE 65536  // 64K memory
static uint8_t memory[MEMORY_SIZE] = {0};

__declspec(dllexport) uint8_t read_memory(uint16_t address) {
    return memory[address];
}

__declspec(dllexport) void write_memory(uint16_t address, uint8_t value) {
    memory[address] = value;
}