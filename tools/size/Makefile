# Makefile for the Universal Run Tool

# Compiler and Flags
CC = gcc
# Use -lrt for clock_gettime, -pthread for future threading, -g for debugging
LDFLAGS = -lrt -pthread
# Strict warnings for high-quality code
# CFLAGS = -Wall -g

# Source files
SRCS = size.c

# Object files derived from source files
OBJS = $(SRCS:.c=.o)

# The final executable name
TARGET = ../../bin/size

# Default target: build the executable
all: $(TARGET)

# Rule to link all object files into the final executable
$(TARGET): $(OBJS)
	$(CC)  -o $(TARGET) $(OBJS) $(LDFLAGS)

# Rule to compile a .c source file into a .o object file
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Target to clean up the build directory
clean:
	rm -f $(OBJS) $(TARGET)

# Phony targets
.PHONY: all clean
