CC = gcc
CFLAGS = -O2 -Wall -m64 -shared
LDFLAGS = -Wl,--export-all-symbols

TARGET_DLLS = memory.dll registers.dll

.PHONY: all clean

all: $(TARGET_DLLS)

memory.dll: memory.c
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $<

registers.dll: registers.c
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $<

clean:
	rm -f *.dll *.o