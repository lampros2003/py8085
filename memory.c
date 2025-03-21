#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define MEMORY_SIZE 65536

typedef struct {
    int8_t data[MEMORY_SIZE];
} Memory;

__declspec(dllexport) Memory* create_memory() {
    Memory* mem = (Memory*)malloc(sizeof(Memory));
    memset(mem->data, 0, MEMORY_SIZE);
    return mem;
}

__declspec(dllexport) void destroy_memory(Memory* mem) {
    free(mem);
}

__declspec(dllexport) int8_t read_memory(Memory* mem, uint16_t address) {
    return mem->data[address];
}

__declspec(dllexport) void write_memory(Memory* mem, uint16_t address, int8_t value) {
    mem->data[address] = value;
}