# File: lib/c_utils/Makefile
# Description: Makefile for building the shared C utility library, now including cJSON.

CC = gcc
AR = ar
CFLAGS = -Wall -Wextra -I. -O2 -fPIC

# List of all source files to be included in the library
SOURCES = sniper_c_utils.c cJSON.c

# Generate object file names from source file names
OBJECTS = $(SOURCES:.c=.o)

# The name of the static library to create
LIBRARY = libsniper_c_utils.a

.PHONY: all clean

# Default target: build the library
all: $(LIBRARY)

# Rule to create the static library from the object files
$(LIBRARY): $(OBJECTS)
	$(AR) rcs $@ $^
	@echo "✓ Shared library $(LIBRARY) created successfully (with cJSON)."

# Rule to compile .c files into .o object files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Target to clean up build artifacts
clean:
	rm -f $(OBJECTS) $(LIBRARY)
	@echo "🧹 Cleaned up c_utils library artifacts."
