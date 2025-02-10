// memory.c
#include <stdint.h>

// 8085 has 64KB of addressable memory
static uint8_t memory[65536];

// Read/write functions
uint8_t read_memory(uint16_t address) {
    return memory[address];
}

void write_memory(uint16_t address, uint8_t value) {
    memory[address] = value;
}